import os
from distutils.core import setup

from fnmatch import fnmatch

from wrairlib.__init__ import __version__

# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def scripts( ):
    return [os.path.join( 'bin', f ) for f in os.listdir( 'bin' ) if not fnmatch( f, '*.swp' )]

# Setup
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
    ],
    scripts = scripts(),
    data_files = [
        ('config',['wrairnaming/conf/formats.cfg',]),
    ],
    requires = [
        "xlwt",
        "numpy (>=1.6)",
        "biopython (>=1.59)",
        "configobj",
    ],
    long_description=read('README.md'),
)
