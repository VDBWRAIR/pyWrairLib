import nose

from StringIO import StringIO
from datetime import date
import string

from ..runfiletitanium import RunFile, RunFileSample

def ere( expect, result ):
    print "Expect: {}".format( expect )
    print "Result: {}".format( result )
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
        
        ere( primerpath, s.primers )
        ere( refpath, s.refgenomelocation )
        ere( usample, s.uniquesampleid )

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
        platform='platform',
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
def parseidline( line ):
    return RunFile( empty_runfile )._parse_id_line( line )

def test_pil_valid():
    ''' Valid date tests '''
    dates = (
        ('13012001',date(2001,01,13)),
        ('13_01_2001',date(2001,01,13)),
        ('2001_01_13',date(2001,01,13)),
    )
    line = "# Run File ID: {}.somedescription"
    for d in dates:
        l = line.format( d[0] )
        pieces = parseidline( l )
        assert pieces['date'] == d[1], "{} != {}".format(pieces['date'],d[1])

def test_pil_emptyline():
    line = ""
    try:
        parseidline( line )
        assert False, "Did not raise ValueError"
    except ValueError as e:
        assert True

def test_pil_invaliddate():
    lines = [
        "# Run File ID: 111979.NonZeroPadded",
        "# Run File ID: 33011979.BadMonth",
        "# Run File ID: 01331979.BadDay", 
        "# Run File ID: 01132001.Wrong",
        "# Run File ID: 01_13_2001.Wrong",
    ]
    for line in lines:
        try:
            parseidline( line )
            assert False, "Did not raise ValueError: " + line
        except ValueError as e:
            assert True

def test_pil_missinghash():
    line = "Run File ID: 01011979.MissingHash"
    try:
        parseidline( line )
        assert False, "Did not raise ValueError"
    except ValueError as e:
        assert True

def test_pil_extraspaces():
    line = "# Run File ID: 01012012.Test 	    "
    parseidline( line )
    assert True

###############################
##### parse_regions_line ######
###############################
def parseregionsline( line ):
    return RunFile( empty_runfile )._parse_regions_line( line )

def test_prl_valid():
    line = "# 2 Region PTP"
    pieces = parseregionsline( line )
    assert pieces == ((1,2), 'PTP'), pieces

def test_prl_empty():
    line = ""
    try:
        parseregionsline( line )
        assert False, 'Did not raise ValueError for empty line'
    except ValueError:
        assert True

def test_prl_missinghash():
    line = "2 Region PTP"
    try:
        parseregionsline( line )
        assert False, 'Did not raise ValueError for missing hash'
    except ValueError:
        assert True

def test_prl_typehasgoofychars():
    rtype = string.printable.replace( '\n', '' )
    line = "# 2 Region " + rtype
    pieces = parseregionsline( line )
    assert pieces == ((1,2), rtype), pieces

def test_prl_zeroregions():
    line = "# 0 Region PTP"
    try:
        parseregionsline( line )
        assert False, 'ValueError not raised for 0 regions'
    except ValueError:
        assert True

###############
#### parse ####
###############

def test_p_valid():
    rf = make_runfile_stringio( platform='platform', regions='2', rtype='PTP', date='01011979', id='testfile', headerline=hdr )
    rf = RunFile( rf )
    assert rf.platform == 'platform'
    assert rf.regions == (1,2)
    assert rf.type == 'PTP'
    assert rf.date == date( 1979, 1, 1 )
    assert rf.id == 'testfile'
    assert len( rf.samples ) == 0
