import tempfile
import os
import os.path
import sys
import glob
import fnmatch
import re
import shutil
from difflib import context_diff
from wrairlib import settings
from copy import deepcopy

def erdiff( expect, result ):
    ''' Expects large strings that have newlines in both expect and result '''
    cd = context_diff( expect.splitlines(True), result.splitlines(True) )
    for line in cd:
        sys.stdout.write( line )
    assert expect == result

def ere( expect, result ):
    er( expect, result )
    # Make sure lists are sorted for comparison
    if isinstance( expect, list ):
        expect = sorted( expect )
        result = sorted( result )
    assert expect == result

def er( expect, result ):
    print "Expected:\n----------\n{}\n------------\n".format( expect )
    print "Result:\n---------\n{}\n------------\n".format( result )

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
