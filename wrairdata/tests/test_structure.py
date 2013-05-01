import nose

import tempfile
import shutil
import os.path
import os
import sys

from ..structure import *
from ..settings import config

class TestDeterminePlatform( object ):
    def setUp( self ):
        self.platforms = config['DEFAULT']['platforms']
        self.tdir = tempfile.mkdtemp()
        self.testdir = os.path.join( self.tdir, 'test' )
        os.mkdir( self.testdir )
        for platform in self.platforms:
            os.mkdir( os.path.join( self.tdir, platform ) )

    def tearDown( self ):
        shutil.rmtree( self.tdir )

    def tst_detect_platform( self, path ):
        for platform in self.platforms:
            chkpath = path.format( platform )
            detected_plat = determine_platform_from_path( chkpath )
            assert detected_plat == platform, "Path(%s): Detected(%s) was not %s" % (path,detected_plat,platform)

    def test_dpfp_relpathbasename( self ):
        ''' Make sure all platforms can be pulled out of rel paths that are basedirs'''
        os.chdir( self.testdir )
        self.tst_detect_platform( '../{}' )

    def test_dpfp_relpathembedded( self ):
        ''' Make sure embedded platform in rel path works '''
        os.chdir( self.testdir )
        self.tst_detect_platform( '../{}/1979_01_01' )

    def test_dpfp_pathbasename( self ):
        ''' Make sure that pathnames are converted to abspaths to be checked for platform '''
        os.chdir( self.tdir )
        self.tst_detect_platform( '{}' )

    def test_dpfp_pathembedded( self ):
        for platform in self.platforms:
            plat_path = os.path.join( self.tdir, platform )
            path = os.path.join( plat_path, '1979_01_01' )
            os.mkdir( path )
            os.chdir( plat_path )
            print "{} should return {}".format( path, platform )
            detected_plat = determine_platform_from_path( '1979_01_01' )
            print "{} should return {}".format( plat_path, platform )
            detected_plat = determine_platform_from_path( '.' )
            assert platform == detected_plat

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
