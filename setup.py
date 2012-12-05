import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description. It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def scripts( ):
    return [os.path.join( 'bin', f ) for f in os.listdir( 'bin' )]

setup(
    name = "wrairlib",
    version = "0.0.1",
    author = "Tyghe Vallard",
    author_email = "vallardt@gmail.com",
    description = ("Various python scripts supporting WRAIR's VDB projects"),
    keywords = "biopython walter reed research python library",
    url = "https://github.com/VDBWRAIR/pyWrairLib",
    packages = ['wrairlib', 'wrairlib.fff', 'wrairlib.parser'],
    scripts = scripts(),
    data_files = [
    ],
    install_requires = [
        "numpy >=1.6",
        "biopython >=1.59"
    ],
    long_description=read('README.md'),
)
