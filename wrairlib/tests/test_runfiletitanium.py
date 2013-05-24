import nose
from nose.tools import eq_, ok_, raises

from StringIO import StringIO
from datetime import date
import string
from difflib import context_diff
import sys

from ..runfiletitanium import RunFile, RunFileSample
from .. import settings

import fixtures

def erdiff( expect, result ):
    ''' Expects large strings that have newlines in both expect and result '''
    cd = context_diff( expect.splitlines(True), result.splitlines(True) )
    for line in cd:
        sys.stdout.write( line )
    assert expect == result

# Mock an empty runfile so we can instantiate the RunFile class
#  without giving it an actual file
empty_runfile = StringIO( "" )

header_template = string.Template('''# $platform sample list
# $regions Region $rtype
# Run File ID: $date.$id
$headerline
$samples''')
hdr = '!Region	Sample_name	Genotype	MIDKey_name	Mismatch_tolerance	Reference_genome_location	Unique_sample_id	Primers'

def make_runfile_stringio( platform, regions, rtype, date, id, headerline=hdr, samples='' ):
    rf = StringIO( header_template.substitute(
        platform=platform,
        regions=regions,
        rtype=rtype,
        date=date,
        id=id,
        headerline=headerline,
        samples=samples)
    )
    return rf

#################### Run File Tests #############################
class TestRunFile( object ):
    def setUp( self ):
        self._supported_date_formats = RunFile.supported_date_formats
        RunFile.supported_date_formats = ('%Y-%m-%d','%d%m%Y','%Y_%m_%d','%d_%m_%Y')
        self.rf = RunFile( StringIO(''), False )
        self.samples = self.fake_samples()
        self.regions = tuple( [int(s.region) for s in self.samples] )
        self.default_kwargs = {
            'regions': self.regions,
            'id': 'Idline',
            'rtype': 'PTP',
            'platform': 'Roche454',
            'date': '2012-05-01',
            'samples': self.samples
        }

    def tearDown( self ):
        RunFile.supported_date_formats = self._supported_date_formats

    def fake_samples( self ):
        REQUIRED_KWARGS = ('region','name','genotype','midkeyname','mismatchtolerance')
        samples = [
            self.fake_sample( name = 'Sample1' ),
            self.fake_sample( reg = '2', name = 'Sample2' )
        ]
        return samples

    def fake_sample( self, reg = '1', name = 'Sample1', gen = 'Den1', mid = 'RL1', mis = 1 ):
        kwargs = dict( zip( RunFileSample.REQUIRED_KWARGS, [reg, name, gen, mid, mis] ) )
        return RunFileSample( **kwargs )

class TestNewRunFile( TestRunFile ):
    def test_new_fromstr( self ):
        ''' Create new runfile from path '''
        for fix in fixtures.RUNFILES:
            RunFile( fix )
    
    def test_new_fromfile( self ):
        ''' Create new runfile from file like object '''
        for fix in fixtures.RUNFILES:
            with open( fix ) as fh:
                RunFile( fh )

    def test_new_autoparse_true( self ):
        ''' autoparse = True '''
        rf = RunFile( fixtures.RUNFILES[0], True )
        assert len( rf.samples ) > 0

    def test_new_autoparse_false( self ):
        ''' autoparse = False '''
        rf = RunFile( fixtures.RUNFILES[0], False )
        print rf.samples
        assert len( rf.samples ) == 0
        rf.parse()
        assert len( rf.samples ) > 0

    def test_new_autoparse_default( self ):
        ''' autoparse = None '''
        rf = RunFile( fixtures.RUNFILES[0] )
        assert len( rf.samples ) > 0

    def test_new_fromkwargs( self ):
        ''' Create new runfile from kwargs '''
        rf = RunFile( **self.default_kwargs )
        for kwa, val in self.default_kwargs.items():
            result = getattr( rf, kwa ) 
            if kwa == 'date':
                result = result.__str__()
            eq_( val, result )

    def test_new_requiredonly( self ):
        ''' Create new runfile from only required kwargs '''
        del self.default_kwargs['rtype']
        del self.default_kwargs['id']
        del self.default_kwargs['regions']
        rf = RunFile( **self.default_kwargs )
        eq_( 'PTP', rf.rtype )
        eq_( 'Description', rf.id )
        eq_( self.regions, rf.regions )
        for kwa, val in self.default_kwargs.items():
            result = getattr( rf, kwa ) 
            if kwa == 'date':
                result = result.__str__()
            eq_( val, result )

    @raises( ValueError )
    def test_new_zerosamples( self ):
        ''' len( samples ) == 0 '''
        self.default_kwargs['samples'] = []
        RunFile( **self.default_kwargs )

    @raises( ValueError )
    def test_new_invalidplatform( self ):
        ''' Platform not in settings '''
        self.default_kwargs['platform'] = 'notinsettings'
        RunFile( **self.default_kwargs )

    @raises( ValueError )
    def test_new_kwargs_invaliddate( self ):
        ''' Invalid date through kwarg '''
        self.default_kwargs['date'] = '99999999'
        RunFile( **self.default_kwargs )

    @raises( ValueError )
    def test_new_invalid_regions1( self ):
        ''' regions is not a sequence of ints or a single int '''
        self.default_kwargs['regions'] = 'a'
        RunFile( **self.default_kwargs )

    @raises( ValueError )
    def test_new_invalid_regions2( self ):
        ''' regions is not a sequence of ints or a single int '''
        self.default_kwargs['regions'] = ['a']
        RunFile( **self.default_kwargs )

class TestFormat( TestRunFile ):
    def setUp( self ):
        self.ht = '{platform},{regions},{rtype},{date},{id}'
        self._HEADER_TEMPLATE = RunFile.HEADER_TEMPLATE
        RunFile.HEADER_TEMPLATE = self.ht
        super( TestFormat, self ).setUp()
        self.default_kwargs['date'] = '2001-01-01'
        eq_( self.rf.HEADER_TEMPLATE, self.ht )

    def tearDown( self ):
        super( TestFormat, self ).tearDown()
        RunFile.HEADER_TEMPLATE = self._HEADER_TEMPLATE

    def test_notset( self ):
        ''' Test rtype, id and regions not being set '''
        del self.default_kwargs['rtype']
        del self.default_kwargs['id']
        del self.default_kwargs['regions']
        rf = RunFile( **self.default_kwargs )
        result = rf.format_header()
        self.default_kwargs['rtype'] = 'PTP'
        self.default_kwargs['id'] = 'Description'
        self.default_kwargs['regions'] = self.regions
        eq_( self.ht.format(**self.default_kwargs), result )

    @raises( ValueError )
    def test_nothingset( self ):
        ''' Test called after autoparse=False and nothing set '''
        self.rf.format_header()

    def test_expected( self ):
        ''' Test expected results '''
        rf = RunFile( **self.default_kwargs )
        expect = self.ht.format(**self.default_kwargs)
        result = rf.format_header()
        eq_( expect, result )

class TestStr( TestRunFile ):
    def test_sameasinputfile( self ):
        ''' Tests that fixture files read in are the same when outputted '''
        for f in fixtures.RUNFILES:
            rf = RunFile( f )
            rf2 = RunFile( StringIO( rf.__str__() ) )
            erdiff( rf.__str__(), rf2.__str__() )

class TestParseIdLine( TestRunFile ):
    def parseidline( self, line ):
        return self.rf._parse_id_line( line )

    def test_pil_valid(self):
        ''' Valid date tests '''
        dates = (
            ('13012001',date(2001,01,13)),
            ('13_01_2001',date(2001,01,13)),
            ('2001_01_13',date(2001,01,13)),
        )
        line = "# Run File ID: {}.somedescription"
        for d in dates:
            l = line.format( d[0] )
            pieces = self.parseidline( l )
            assert pieces['date'] == d[1], "{} != {}".format(pieces['date'],d[1])

    def test_pil_emptyline(self):
        line = ""
        try:
            self.parseidline( line )
            assert False, "Did not raise ValueError"
        except ValueError as e:
            assert True

    def test_pil_invaliddate(self):
        lines = [
            "# Run File ID: 111979.NonZeroPadded",
            "# Run File ID: 33011979.BadMonth",
            "# Run File ID: 01331979.BadDay", 
            "# Run File ID: 01132001.Wrong",
            "# Run File ID: 01_13_2001.Wrong",
        ]
        for line in lines:
            try:
                self.parseidline( line )
                assert False, "Did not raise ValueError: " + line
            except ValueError as e:
                assert True

    def test_pil_missinghash(self):
        line = "Run File ID: 01011979.MissingHash"
        try:
            self.parseidline( line )
            assert False, "Did not raise ValueError"
        except ValueError as e:
            assert True

    def test_pil_extraspaces(self):
        line = "# Run File ID: 01012012.Test 	    "
        self.parseidline( line )
        assert True
        
########################################################################

#################### Run File Sample Tests #############################
class TestRunFileSample( object ):
    def setUp( self ):
        self.date = date( 2011, 01, 01 )
        self.kwargs = dict(
            region = 1,
            name = 'Sample1',
            genotype = 'Den3',
            midkeyname = 'RL1',
            mismatchtolerance = 1,
            refgenomelocation = 'User_defined_Reference',
            uniquesampleid = 'Sample1',
            primers = 'User_defined_primers',
            date = self.date 
        )

class TestNewSample( TestRunFileSample ):
    ''' Test RunFileSample instantiation '''
    def test_createsample( self ):
        ''' Test creating sample from column delimiated string as well as arguments'''
        s1 = RunFileSample( **self.kwargs )
        s2 = RunFileSample( s1.__str__(), self.date )
        for kwarg, value in self.kwargs.items():
            print "Expect: {}->{}".format(kwarg,value)
            print "Result: {}->{}".format(kwarg,getattr(s2,kwarg))
            assert value, getattr(s2,kwarg)

    def test_createsample_invaliddate( self ):
        ''' Make sure invalid dates raise ValueError '''
        self.kwargs['date'] = 'Imastringnotadate'
        try:
            RunFileSample( **self.kwargs )
            assert False, "Date string did not raise an exception"
        except ValueError as e:
            assert True
        
    def test_createsample_validdate( self ):
        ''' Make sure valid date works '''
        s = RunFileSample( **self.kwargs )
        assert s.date == self.date

    def test_createsample_fromrow_extraspaces( self ):
        ''' Ensure extra spaces at the end don't break anything '''
        sstr = RunFileSample( **self.kwargs ).__str__()
        sstr += ' 	'
        s = RunFileSample( sstr, self.date )
        for kwarg, value in self.kwargs.items():
            print "Expect: {}->{}".format(kwarg,value)
            print "Result: {}->{}".format(kwarg,getattr(s,kwarg))
            assert value, getattr(s,kwarg)

    def test_createsample_strip( self ):
        ''' Make sure whitespace is stripped from every column '''
        sstr = RunFileSample( **self.kwargs ).__str__()
        sstr = sstr.replace( '\t', ' \t ' )
        s = RunFileSample( sstr, self.date )
        for kwarg, value in self.kwargs.items():
            expect = getattr(s,kwarg)
            if kwarg in ('primers','refgenomelocation'):
                print "Expecting {} to be None. Got ->{}<-".format(kwarg,expect)
                assert expect is None
                continue
            print "Attribute: {}".format(kwarg)
            print "Expect:->{}<-".format(value)
            print "Result:->{}<-".format(expect)
            assert value == expect

    def test_createsample_missing( self ):
        ''' Test missing required values '''
        del self.kwargs['name']
        del self.kwargs['region']
        del self.kwargs['genotype']
        del self.kwargs['midkeyname']
        del self.kwargs['mismatchtolerance']
        del self.kwargs['date']
        try:
            RunFileSample( **self.kwargs )
            assert False, "Missing required arguments did not raise exception"
        except ValueError as e:
            assert True

    def test_createsample_optional( self ):
        ''' Test optional reference, uname and primers '''
        del self.kwargs['refgenomelocation']
        del self.kwargs['uniquesampleid']
        del self.kwargs['primers']
        s = RunFileSample( **self.kwargs )
        print s.primers
        assert s.primers is None
        print s.refgenomelocation
        assert s.refgenomelocation is None
        print s.uniquesampleid
        assert s.uniquesampleid == s.name

    def test_createsample_optional_set( self ):
        refpath = '/some/path/ref.fna'
        primerpath = '/some/path/primer.fna'
        usample = 'Sample1Unique'
        self.kwargs['refgenomelocation'] = refpath
        self.kwargs['primers'] = primerpath
        self.kwargs['uniquesampleid'] = usample
        s = RunFileSample( **self.kwargs )
        
        eq_( primerpath, s.primers )
        eq_( refpath, s.refgenomelocation )
        eq_( usample, s.uniquesampleid )

    def test_createsample_disabled( self ):
        ''' Create a disabled sample '''
        self.kwargs['disabled'] = True
        s = RunFileSample( **self.kwargs )
        assert s.disabled

    def test_createsample_enabled( self ):
        ''' Just to make sure '''
        self.kwargs['disabled'] = False
        s = RunFileSample( **self.kwargs )
        assert not s.disabled

class TestSampleLine( TestRunFileSample ):
    '''
        Test Creating samples from template
        it is just a simple string format
    '''
    def test_str_disabled( self ):
        ''' Make sure disabled has # in front '''
        rowstr = '#' + RunFileSample.SAMPLE_TEMPLATE.format( **self.kwargs )
        s = RunFileSample( rowstr, self.date )
        assert s.__str__().startswith( '#' )

    def test_str_noref( self ):
        ''' Make sure User_defined_Reference is present '''
        rowstr = RunFileSample.SAMPLE_TEMPLATE.format( **self.kwargs )
        s = RunFileSample( rowstr, self.date )
        assert RunFileSample.NULL_REFERENCE_STR in s.__str__()

    def test_str_noprimer( self ):
        ''' Make sure User_defined_primers is present '''
        rowstr = RunFileSample.SAMPLE_TEMPLATE.format( **self.kwargs )
        s = RunFileSample( rowstr, self.date )
        assert RunFileSample.NULL_REFERENCE_STR in s.__str__()

#######################################################################

#######################
## samples property ###
#######################
def test_samples( ):
    samples = '''1	Sample1	Virus	TI001	0	VOID	Sample1	VOID
1	Sample2	Virus	TI002	0	VOID	Sample2	VOID
#2	Sample3	Virus	TI001	0	VOID	Sample3	VOID
2	Sample4	Virus	TI002	0	VOID	Sample4	VOID
'''
    rf = make_runfile_stringio(
        platform='Roche454',
		regions='2',
		rtype='PTP',
		date='01011979',
		id='testfile',
		headerline=hdr,
		samples=samples
    )
    rf = RunFile( rf )
    assert len( rf.samples ) == 3, "Should be %s samples. Got %s" % (len( rf.samples ), rf.samples)
    assert len( rf[1] ) == 2
    assert len( rf[2] ) == 1

##########################
##### parse_id_line ######
##########################


###############################
##### parse_regions_line ######
###############################
class TestParseRegionLine( TestRunFile ):
    def parseregionsline( self, line ):
        return self.rf._parse_regions_line( line )

    def test_prl_valid(self):
        line = "# 2 Region PTP"
        pieces = self.parseregionsline( line )
        print line
        print pieces
        eq_( pieces, (2, 'PTP') )

    def test_region_single_str( self ):
        ''' Make sure str works '''
        self.rf.regions = '1'
        eq_( self.rf.regions, (1,) )

    def test_region_liststr( self ):
        ''' Make sure list of strings work '''
        self.rf.regions = ['1','2']
        eq_( self.rf.regions, (1,2) )

    def test_region_int( self ):
        ''' Make sure setting as int works '''
        self.rf.regions = 1
        eq_( self.rf.regions, (1,) )
        self.rf.regions = 2
        eq_( self.rf.regions, (1,2) )

    @raises( ValueError )
    def test_region_emptylist( self ):
        ''' Make sure empty list raises error '''
        self.rf.regions = []

    def test_region_listint( self ):
        ''' Make sure list of ints works '''
        self.rf.regions = [1,2]
        eq_( self.rf.regions, (1,2) )

    def test_region_tuple( self ):
        ''' Make sure tuple of ints works '''
        self.rf.regions = (1,2)
        eq_( self.rf.regions, (1,2) )
    
    def test_region_tuplestr( self ):
        ''' Make sure str of tuples gets parsed '''
        self.rf.regions = ('1','2')
        eq_( self.rf.regions, (1,2) )

    @raises( ValueError )
    def test_region_emptyseq( self ):
        ''' Make sure empty seqs raises error '''
        self.rf.regions = ()

    @raises( ValueError )
    def test_prl_empty(self):
        ''' Make sure empty region line raises Exception '''
        line = ""
        print line
        print self.parseregionsline( line )
    
    @raises( ValueError )
    def test_prl_missinghash(self):
        ''' Region Line Needs to have the hash '''
        line = "2 Region PTP"
        print line
        print self.parseregionsline( line )

    def test_prl_typehasgoofychars(self):
        ''' Type should support any characters in string '''
        rtype = string.printable.replace( '\n', '' )
        line = "# 2 Region " + rtype
        pieces = self.parseregionsline( line )
        print line
        print pieces
        eq_( pieces, (2, rtype) )

    @raises( ValueError )
    def test_prl_zeroregions(self):
        ''' Make sure that 0 for regions raises exception '''
        self.rf.regions = 0
