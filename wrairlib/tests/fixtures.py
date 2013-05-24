import os
import os.path
import glob

PATH = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ), 'fixtures' )

RUNFILES = glob.glob( os.path.join( PATH, 'Run*' ) )
