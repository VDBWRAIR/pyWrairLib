import nose
import tempfile
import os
import os.path
import shutil
from datetime import date

from .. import util

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

class TestGetAllSff( object ):
    def setup( self ):
        self.tempdir = tempfile.mkdtemp()
        print "Created " + self.tempdir

    def teardown( self ):
        print "Removing tree " + self.tempdir
        shutil.rmtree( self.tempdir )

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
    
def test_dsn( ):
    rf = Mock()
    rf.date = date( 1979, 1, 1 )
    s1 = Mock()
    s1.runfile = rf
    s1.name = 'Sample1'
    s1.midkeyname = 'TI001'
    s1.genotype = 'Virus'

    newname = util.demultiplex_sample_name( s1, 'Roche454' )
    assert newname == '{}__{}__{}__{}.sff'.format( s1.name, s1.midkeyname, rf.date.strftime( '%Y_%m_%d' ), s1.genotype )

def test_r( ):
    pass
