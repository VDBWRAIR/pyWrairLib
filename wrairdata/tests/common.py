import tempfile
import os
import os.path
import sys
import glob
import fnmatch
import re
import shutil

def ere( expect, result ):
    er( expect, result )
    # Make sure lists are sorted for comparison
    if isinstance( expect, list ):
        expect = sorted( expect )
        result = sorted( result )
    assert expect == result

def er( expect, result ):
    print "Expected: {}".format( expect )
    print "Result: {}".format( result )

def create( filepath ):
    ''' Just create an empty file '''
    open( filepath, 'w' ).close()

class BaseClass( object ):
    def setUp( self ):
        ''' Ensure there is a tempdir and we have changed directory to it '''
        self.tempdir = tempfile.mkdtemp()
        os.chdir( self.tempdir )

    def tearDown( self ):
        shutil.rmtree( self.tempdir )

    def create_( self, path, t ):
        t = t.lower()
        if t == 'dir':
            os.mkdir( path )
        elif t == 'file':
            open( path, 'w' ).close()
        elif t == 'link':
            open( path+'link', 'w' ).close()
            os.symlink( path+'link', path )
