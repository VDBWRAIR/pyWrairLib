import nose
import tempfile
import os
import os.path
import shutil
from datetime import date
from configobj import ConfigObj

from .. import util
from common import BaseClass, ere, create
import fixtures

# Shortcuts
gms = util.get_multiplexed_sffs
gsf = util.get_sff_files
class MultiplexedSffs( BaseClass ):
    ''' Base class for multiplexed sff testing '''
    def create_and_tst( self, func, sfflist, expectlist, createdir=None ):
        ''' Create files in sfflist and then test '''
        if createdir is None:
            createdir = self.tempdir
        for f in sfflist:
            create( f )
        sffs = func( createdir )
        ere( expectlist, sffs )

class TestMultiplexedSffs( MultiplexedSffs ):
    ''' get_multiplexed_sffs tests '''
    def test_lowercase( self ):
        ''' Make sure lowercase are not returned '''
        self.create_and_tst( gms, ['fake01.sff'], [] )

    def test_singledigit( self ):
        ''' Single digit files should not be returned '''
        self.create_and_tst( gms, ['FAKE1.sff'], [] )

    def test_mixedfiles( self ):
        ''' Make sure only correctly formatted are returned '''
        self.create_and_tst( gms, ['FAKE01.sff','fake01.sff'], [os.path.join( self.tempdir, 'FAKE01.sff' )] )

    def test_emptysffdir( self ):
        ''' Double check empty dir works '''
        self.create_and_tst( gms, [], [] )

    def test_correctamount( self ):
        ''' Make sure the correct ammount are returned '''
        sfflst = ["FAKE{:02}.sff".format(i) for i in range(1,4)]
        expected = [os.path.abspath( sff ) for sff in sfflst]
        self.create_and_tst( gms, sfflst, expected )

class TestGetSffFiles( MultiplexedSffs ):
    ''' get_sff_files tests '''
    def test_lowercase( self ):
        ''' Ensure lowercase are not returned '''
        self.create_and_tst( gsf, ['fake1.sff'], [] )
        
    def test_singledigit( self ):
        ''' Ensure 2 digits are enforced '''
        self.create_and_tst( gsf, ['FAKE1.sff'], [] )

    def test_mixedfiles( self ):
        ''' Ensure only correctly named are returned in a mixed set '''
        self.create_and_tst( gsf, ['FAKE01.sff','fake01.sff'], {1:os.path.join( self.tempdir, 'FAKE01.sff' )} )

    def test_emptydir( self ):
        ''' Just make sure empty dir returns empty dict '''
        self.create_and_tst( gsf, [], [] )

    def test_correct( self ):
        ''' Test dir of all correctly named '''
        sfflst = ["FAKE{:02}.sff".format(i) for i in range(1,4)]
        expected = {int(os.path.splitext(sff)[0][-2:]):os.path.abspath(sff) for sff in sfflst}
        self.create_and_tst( gsf, sfflst, expected )

def fake_sff_dir( prefix='FAKE0', numsff=2 ):
    # Fake demultiplexed dir
    sff_dir = tempfile.mkdtemp()
    # Touch some fake sff files
    for i in range( 1, numsff+1 ):
        open( os.path.join( sff_dir, prefix + str(i) + '.sff' ), 'w' ).close()
    return sff_dir

def test_gsf( ):
    num = 4
    sff_dir = fake_sff_dir( numsff=num )
    sff_files = util.get_sff_files( sff_dir )
    for i in range( 1, num+1 ):
        path = os.path.join( sff_dir, 'FAKE0' + str(i) + '.sff' ) 
        try:
            compare_path = sff_files[i]
        except KeyError as e:
            assert False, "%s should contain %s" % (sff_files,path)
        assert compare_path == path, "%s should be %s" % (sff_files[i],path)
    shutil.rmtree( sff_dir )

class TestEnsureValidAbsPath( BaseClass ):
    typesgood = ('dir','file','link','Dir','DIR')
    typesbad = ('mount','abs','turkey')

    def pathtest( self, path, t, expect ):
        print "Path: {}".format(path)
        print "Type: {}".format(t)
        result = util.is_valid_abs_path( path, t )
        ere( expect, result )

    def pathtestall( self, path, expect ):
        print "BasePath: {}".format(path)
        for t in self.typesgood:
            self.pathtest( path, t, expect )

    def test_eavp_abspathvalid( self ):
        ''' Valid abs path should return True '''
        os.chdir( self.tempdir )
        for t in self.typesgood:
            cname = 'test'+t
            self.create_( cname, t )
            print os.listdir( '.' )
            self.pathtest( os.path.abspath( cname ), t, True )

    def test_eavp_abspathinvalid( self ):
        ''' Invalid abs path should return False '''
        self.pathtestall( '/bogus/path/sjdhwu8dfs8wn', False )
        
    def test_eavp_relpathvalid( self ):
        ''' Valid relative path should return False '''
        os.chdir( self.tempdir )
        os.mkdir( 'test' )
        self.pathtestall( 'test', False )

    def test_eavp_relpathinvalid( self ):
        ''' Invalid relative path should return False '''
        self.pathtestall( 'bogus/path/sjaneuwjfhsue', False )

class TestSetPerms( BaseClass ):
    '''
        Not testing gid, uid perms change on purpose
        since they depend on having root permissions
    '''
    def test_recursive( self ):
        ''' Make sure recursive works '''
        # Create files rw-r--r-- and folders rwxr-xr-x
        os.umask( 0022 )
        self.create_( 'subdir', 'dir' )
        self.create_( 'file', 'file' )
        self.create_( os.path.join( 'subdir', 'subsubdir' ), 'dir' )
        self.create_( 'link', 'link' )
        util.set_perms( self.tempdir, '766', recursive=True )

class TestGetAllSff( BaseClass ):
    def fake_demultiplex_dir( self, name='454Reads.{}.sff', regions=2, num=3 ):
        # Make fake demultiplex top level dir
        ddir = self.tempdir
        for i in range( 1, regions+1):
            # Make region dir
            rdir = os.path.join( ddir, str( i ) )
            os.mkdir( rdir )
            for si in range( 1, num+1 ):
                # Touch fake sff file
                fake_sff = os.path.join( rdir, name.format( si ) )
                open( fake_sff, 'w' ).close()
        return ddir

    def demultiplex_dir( self, sff_name_format, num_regions, num_sff_files ):
        ddir = self.fake_demultiplex_dir( sff_name_format, num_regions, num_sff_files )
        region_files = util.get_all_sff( ddir )
        
        for region_dir, sff_files in region_files.items():
            for i, filename in enumerate( sff_files, 1 ):
                expected_name = os.path.join( ddir, str(region_dir), sff_name_format.format( i ) )
                assert expected_name in sff_files, "%s should exist in %s" % (expected_name, sff_files )

    def test_gas1( self ):
        ''' Test edge case 1 region 0 files '''
        self.demultiplex_dir( '454Reads.{}.sff', 1, 0 )

    def test_gas2( self ):
        ''' Test edge case 1 region > 0 files '''
        self.demultiplex_dir( '454Reads.{}.sff', 1, 2 )

    def test_gas3( self ):
        ''' Test edge case > 1 region 0 files '''
        self.demultiplex_dir( '454Reads.{}.sff', 4, 0 )

    def test_gas4( self ):
        ''' Test edge case > 1 region > 0 files '''
        self.demultiplex_dir( '454Reads.{}.sff', 4, 2 )

def test_rss( ):
    ''' This doesn't need to be tested '''
    pass

def test_rftsm( ):
    pass

class Mock():
    def __setattr__( self, name, value ):
        self.__dict__[name] = value
    
class TestDemultiplexSampleName( object ):
    def setUp( self ):
        # This is some wanky hack to fix a problem that I'm
        # not sure why it is happening.
        # the config changes from other tests are being seen here
        # so this hack replaces the config for the util module
        # with a very fresh version
        from wrairlib.settings import path_to_config, parse_config
        util.config = parse_config( path_to_config )

    def test_dsn( self ):
        rf = Mock()
        rf.date = date( 1979, 1, 1 )
        s1 = Mock()
        s1.runfile = rf
        s1.name = 'Sample1'
        s1.midkeyname = 'TI001'
        s1.genotype = 'Virus'
        s1.region = 1

        print util.config
        newname = util.demultiplex_sample_name( s1, 'Roche454' )
        nn = util.config['Platforms']['Roche454']['read_out_format']
        assert newname == nn.format( samplename=s1.name, 
                                     region=s1.region,
                                     midkey=s1.midkeyname,
                                     date=rf.date.strftime( '%Y_%m_%d' ),
                                     virus=s1.genotype,
                                     extension='sff' )

class TestGetFile( BaseClass ):
    def test_getall( self ):
        os.mkdir( 'files' )
        os.chdir( 'files' )
        fs = ('file1.txt','file2.txt')
        files = {f:os.path.abspath(f) for f in fs}
        # Touch all the files
        [open(f,'w').close() for f in files]
        ere( sorted(files.values()), sorted(util.get_all_( os.getcwd(), '*.txt' )) )
        # Make sure non current dir works
        os.chdir( self.tempdir )
        ere( sorted(files.values()), sorted(util.get_all_( 'files', '*.txt' )) )

    def test_getallblank( self ):
        ere( [], util.get_all_( '.', '*' ) )
        open( 'file','w' ).close()
        ere( [], util.get_all_( '.', '*.txt' ) )

def mock_sample( name, midkeyname, genotype, region, rf ):
    s = Mock()
    s.name = name
    s.midkeyname = midkeyname
    s.genotype = genotype
    s.region = region
    s.runfile = rf
    return s

class TestRunfileMapping( BaseClass ):
    def test_correctmapping( self ):
        runfile = Mock()
        runfile.date = date( 2013, 05, 01 )
        runfile.regions = [1,2]
        runfile.platform = 'Roche454'
        r1s1 = mock_sample( 'Sample1', 'RL1', 'pH1N1', 1, runfile )
        r1s2 = mock_sample( 'Sample2', 'RL2', 'pH1N1', 1, runfile )
        r2s1 = mock_sample( 'Sample1', 'RL1', 'pH1N1', 2, runfile )
        r2s2 = mock_sample( 'Sample2', 'RL2', 'pH1N1', 2, runfile )
        runfile.samples = [r1s1,r1s2,r2s1,r2s2]
        result = util.runfile_to_sfffile_mapping( runfile )
        mp = fixtures.MIDPREFIX
        expect = {1:{'454Reads.'+mp+'RL1.sff':'Sample1__1__RL1__2013_05_01__pH1N1.sff', '454Reads.'+mp+'RL2.sff':'Sample2__1__RL2__2013_05_01__pH1N1.sff'},2:{'454Reads.'+mp+'RL1.sff':'Sample1__2__RL1__2013_05_01__pH1N1.sff', '454Reads.'+mp+'RL2.sff':'Sample2__2__RL2__2013_05_01__pH1N1.sff'}}
        ere( expect, result )
