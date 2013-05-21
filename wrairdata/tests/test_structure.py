import nose

import tempfile
import shutil
import os.path
import os
import sys
from glob import glob
import fnmatch
from copy import deepcopy

from common import BaseClass, ere
import common

from ..structure import *
from .. import structure
class SBaseClass( BaseClass ):
    def setUp( self ):
        super( SBaseClass, self ).setUp()
        # Changing the config the way that it is done is residual so we deepcopy it
        # and restore it on teardown
        self.orig_config = deepcopy( structure.config )
        self.ngsdir = os.path.join( self.tempdir, 'ngsdir' )
        self.readsbysampledir = os.path.join( self.ngsdir, 'readsbysample' )
        self.rawdatadir = os.path.join( self.ngsdir, 'rawdatadir' )
        self.readdatadir = os.path.join( self.ngsdir, 'readdatadir' )
        self.platforms = ['Plat1','Plat2']
        self.readinformat = '(?P<samplename>\w+_\d).(?P<ext>.*)'
        self.readoutformat = '{name}_{ext}'
        self.struct_config = {
            'Paths': {
                'NGSDATA_DIR': self.ngsdir,
                'DataDirs': {
                    'READSBYSAMPLE_DIR': self.readsbysampledir,
                    'RAWDATA_DIR': self.rawdatadir,
                    'READDATA_DIR': self.readdatadir
                }
            },
            'Platforms': { 
                pn: {'read_in_format':self.readinformat.format(pn), 'read_out_format':self.readoutformat} for pn in self.platforms
            }
        }
        structure.config['Paths'] = self.struct_config['Paths']
        structure.config['Platforms'] = self.struct_config['Platforms']

    def tearDown( self ):
        super( SBaseClass, self ).tearDown()
        structure.config = self.orig_config

class TestCreateDirStructure( SBaseClass ):
    def setUp( self ):
        super( TestCreateDirStructure, self ).setUp()

    def test_create_platform_dirs( self ):
        ''' Test create_platform_dirs '''
        structure.create_platform_dirs( self.tempdir )
        ps = os.listdir( self.tempdir )
        print "Expecting: {}".format( self.platforms )
        print "Result: {}".format( ps )
        assert ps == self.platforms

    def test_ngs_dir( self ):
        ''' Test create_ngs_dir '''
        structure.create_ngs_dir()
        print os.listdir( self.tempdir )
        assert os.path.isdir( self.ngsdir )

    def test_create_directory_structure( self ):
        ''' Ensure DataDirs are created, each with platforms in them '''
        structure.create_directory_structure()
        print os.listdir( self.tempdir )
        assert os.path.isdir( self.ngsdir )
        for name, path in structure.config['Paths']['DataDirs'].items():
            if name == 'READSBYSAMPLE_DIR':
                ere( True, os.path.isdir( path ) )
                result = os.listdir( path )
                expected = []
                ere( expected, result )
                continue
            plats = os.listdir( path )
            expected=structure.config['Platforms'].keys()
            ere( expected, plats )

    def test_dirsexist( self ):
        ''' If directories exist then don't recreate them '''
        structure.create_directory_structure()
        try:
            structure.create_directory_structure()
            assert True
        except OSError as e:
            print e
            assert False, "OSError raised when directories already exist"

class TestDeterminePlatform( SBaseClass ):
    def setUp( self ):
        super( TestDeterminePlatform, self ).setUp()
        self.testdir = os.path.join( self.tempdir, 'test' )
        os.mkdir( self.testdir )
        structure.create_directory_structure()

    def tst_detect_platform( self, path ):
        for platform in self.platforms:
            chkpath = path.format( platform )
            detected_plat = determine_platform_from_path( chkpath )
            ere( platform, detected_plat )

    def test_dpfp_relpathbasename( self ):
        ''' Make sure all platforms can be pulled out of rel paths that are basedirs'''
        self.tst_detect_platform( '../{}' )

    def test_dpfp_relpathembedded( self ):
        ''' Make sure embedded platform in rel path works '''
        self.tst_detect_platform( '../{}/1979_01_01' )

    def test_dpfp_pathbasename( self ):
        ''' Make sure that pathnames are converted to abspaths to be checked for platform '''
        self.tst_detect_platform( '{}' )

    def test_dpfp_pathembedded( self ):
        for rdir in (self.readdatadir, self.rawdatadir):
            for platform in self.platforms:
                plat_path = os.path.join( rdir, platform )
                path = os.path.join( plat_path, '1979_01_01' )
                os.mkdir( path )
                os.chdir( plat_path )
                detected_plat = determine_platform_from_path( '1979_01_01' )
                ere( platform, detected_plat )
                detected_plat = determine_platform_from_path( '.' )
                ere( platform, detected_plat )

    def test_dpfp_abspathbasename( self ):
        self.tst_detect_platform( '/abspath/{}' )

    def test_dpfp_abspathembedded( self ):
        self.tst_detect_platform( '/abspath/{}/1979_01_01' )

    def test_dpfp_missingplatform( self ):
        for platform in self.platforms:
            try:
                determine_platform_from_path( '/some/path' )
                assert False, "Missing platform did not raise an exception"
            except ValueError as e:
                assert True

class TestLinkReads( SBaseClass ):
    def test_mpfd( self ):
        result = structure.match_pattern_for_datadir( '/some/path/Plat1/file' )
        expected = self.readinformat.format( 'Plat1' )
        ere( expected, result )

    def test_lrbs( self ):
        ''' Make sure that any list of valid reads get linked '''
        structure.create_directory_structure()
        rfs = ('sample_1.ab1','sample_1.sff','sample_1.fastq','sample_2.fastq','readme.txt')
        expected_dirs = {'sample_1': ['sample_1.ab1','sample_1.fastq','sample_1.sff'], 'sample_2':['sample_2.fastq']}
        outpaths = []
        # Touch all the read filenames inside of each platform
        for plat in self.platforms:
            for read in rfs:
                rpath = os.path.join( self.readdatadir, plat, read )
                outpaths.append( rpath )
                common.create( rpath )
            # This should link all of the outpaths into the readsbysampledir
            platpath = os.path.join( self.readdatadir, plat )
            structure.link_reads_by_sample( platpath, self.readsbysampledir )
        print "Paths touched: {}".format(outpaths)
        # Now there should be directories for each read
        sampledirs = os.listdir( self.readsbysampledir )
        ere( expected_dirs.keys(), sampledirs )
        for sample,expectedfiles in expected_dirs.items():
            resultfiles = os.listdir( os.path.join( self.readsbysampledir, sample ) )
            ere( expectedfiles, resultfiles )

    def test_linkreadsbysample_multidir( self ):
        ''' Make sure a directory with directories containing reads works '''
        structure.create_directory_structure()
        plat = self.platforms[0]
        platd = os.path.join( self.readdatadir, plat )
        ddir = os.path.join( platd, 'demultiplexed' )
        os.chdir( platd )
        # Make some fake region dirs
        os.makedirs( os.path.join( ddir, '1' ) )
        os.makedirs( os.path.join( ddir, '2' ) )
        rfs = ('sample_1.ab1','sample_1.sff','sample_1.fastq','sample_2.fastq','readme.txt')
        fake_samples = {'1':rfs,'2':rfs}
        # Populate fake regions
        for reg, samples in fake_samples.items():
            for sample in samples:
                common.create( os.path.join( ddir, reg, reg+sample ) )
            print os.listdir( os.path.join( ddir, reg ) )

        structure.link_reads_by_sample( ddir, self.readsbysampledir )
        os.chdir( self.readsbysampledir )
        for reg, samples in fake_samples.items():
            print os.listdir( self.readsbysampledir )
            for sample in samples:
                if 'readme.txt' in sample:
                    continue
                dname, ext = os.path.splitext( sample )
                assert os.path.isdir( reg+dname ), "Read directory {} doesn't exist".format(reg+dname)

    def test_linkreadbysample_nonabs( self ):
        read_path = os.path.relpath( os.path.join( self.readdatadir, 'Plat1', 'sample_1.sff' ) )
        cpat = re.compile( self.readinformat )
        expect = ['sample_1']
        self.linkreadbysample_tst( read_path, cpat, expect )

    def test_linkreadbysample_invalidread( self ):
        read_path = os.path.join( self.readdatadir, 'Plat1', 'invalid.txt' )
        cpat = re.compile( self.readinformat )
        expect = []
        self.linkreadbysample_tst( read_path, cpat, expect )

    def linkreadbysample_tst( self, read_path, cpat, expect ):
        structure.create_directory_structure()
        print os.getcwd()
        print os.listdir( '.' )
        open( read_path, 'w' ).close()
        structure.link_read_by_sample( read_path, self.readsbysampledir, cpat )
        result = os.listdir( self.readsbysampledir )
        # Make sure sample name dir creates
        ere( expect, result )
        # Make sure samples get linked
        if expect:
            for ed in expect:
                for sl in glob( os.path.join( ed, '*' ) ):
                    linkpath = os.readlink( sl )
                    ere( read_path, linkpath )
