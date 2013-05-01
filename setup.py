import os
from distutils.core import setup

from fnmatch import fnmatch
import subprocess
import sys

# The major.minor version number
__version__ = 0

# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def scripts( ):
    return [os.path.join( 'bin', f ) for f in os.listdir( 'bin' ) if not fnmatch( f, '*.swp' )]

def set_version():
    if not os.path.isdir(".git"):
        print "This does not appear to be a Git repository."
        return
    try:
        p = subprocess.Popen(["git", "describe", "--tags", "--always"], stdout=subprocess.PIPE)
    except EnvironmentError:
        print "unable to run git"
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print "unable to run git"
        return

    with open( '_version.py', 'w' ) as fh:
        global __version__
        __version__ = stdout.strip()
        fh.write( "__version__ = '%s'\n" % __version__ )

    return True

# Setup
if set_version() is None:
    sys.exit( -1 )

setup(
    name = "pyWrairLib",
    version = __version__,
    author = "Tyghe Vallard",
    author_email = "vallardt@gmail.com",
    description = ("Various python scripts supporting WRAIR's VDB projects"),
    keywords = "biopython walter reed research python library",
    url = "https://github.com/VDBWRAIR/pyWrairLib",
    packages = [
        'wrairlib', 
        'wrairlib.parser',
        'wrairlib.blastresult',
        'wrairdata',
        'wrairnaming',
        'wrairnaming.schemes',
        'wrairanalysis',
    ],
    scripts = scripts(),
    data_files = [
        ('config',['config/settings.cfg',]),
    ],
    requires = [
        "xlwt",
        "numpy (>=1.6)",
        "biopython (>=1.59)",
        "configobj",
    ],
    long_description=read('README.md'),
)
