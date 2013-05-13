##################################################################
## Data directory structure library
##################################################################

import os
import os.path
import sys
import re
import logging
from glob import glob
from copy import deepcopy

from wrairlib.settings import config
from util import *

def determine_platform_from_path( datapath ):
    '''
        Given a read data or raw data path extract the platform from it
        I.E: NGSData/ReadData/Sanger/2013_04_02 would return Sanger
    '''
    abs_datapath = os.path.abspath( datapath )
    platform_pat = "(" + "|".join( get_platforms().keys() ) + ")"
    m = re.search( platform_pat, abs_datapath )
    if m:
        platform = m.groups(0)[0]
        logging.debug( "Platform detected as: %s" % platform )
        return platform
    else:
        raise ValueError( "%s does not have a valid platform in it" % datapath )

def match_pattern_for_datadir( datadir ):
    ''' Determine platform from path then return key from dictionary '''
    platform = determine_platform_from_path( datadir )
    pattern = config['Platforms'][platform]['read_in_format']
    logging.debug( "Using file matching pattern: %s" % pattern )
    return pattern

def link_reads_by_sample( datadir, outputbase ):
    '''
        Given a datadir with read files in it, link all valid
        reads for the platform detected from its path into
        outputbase. Each read file that is valid will have the samplename
        extracted from its name and a directory created for it in outputbase
    '''
    if not is_valid_abs_path( datadir, 'dir' ):
        raise ValueError( "{} is not a valid abs path".format( datadir ) )
    if not is_valid_abs_path( outputbase, 'dir' ):
        raise ValueError( "{} is not a valid abs path".format( outputbase ) )

    logging.debug( "Linking Reads from {} into {}".format( datadir, outputbase ) )
    # Get platform to determine how to fetch read files
    platform = determine_platform_from_path( datadir )
    # Fetch the correct pattern for the platform
    pattern = match_pattern_for_datadir( datadir )
    # Compile the match pattern
    cpattern = re.compile( pattern )

    for read in get_all_( datadir, '*' ):
        link_read_by_sample( read, outputbase, cpattern )

def link_sffreads_by_sample( datadir, outputbase, cpattern ):
    # Loop through every sff file
    for region, sfffiles in get_all_sff( datadir ).items():
        for sfffile in sfffiles:
            link_read_by_sample( sfffile, outputbase, cpattern )

def link_read_by_sample( readfilepath, outputbase, matchpattern ):
    '''
        Given a single read file link it to its appropriate sample directory
        inside of the READSBYSAMPLE_DIR
        Matchpattern is the compiled re pattern to make sure the filename matches to
    '''
    # Ensure readfile is absolute path
    if not os.path.isabs( readfilepath ):
        readfilepath = os.path.abspath( readfilepath )

    # Get just the basename of the filepath
    readfile = os.path.basename( readfilepath )

    # Attempt the file pattern match
    m = matchpattern.match( readfile )
    if m is None:
        logging.warning( "Name scheme used: {}".format( matchpattern.pattern ) )
        logging.warning( "Read file %s does not conform to the naming scheme in settings file." % readfile )
        logging.warning( "It will be skipped" )
        return

    # Get the file info from the name of the file
    fileinfo = m.groupdict()
    logging.debug( "Filename info: %s" % fileinfo )

    # The path to the symlink
    # <outputbase>/<samplename>/<orig filename>
    samplenamedir = os.path.join( outputbase, fileinfo['samplename'] )
    dst = os.path.join( samplenamedir, readfile )
    logging.debug( "Destination for symlink: %s" % dst )

    # Make sure samplenamedir exists
    if not os.path.exists( samplenamedir ):
        logging.info( "Creating samplename directory %s" % samplenamedir )
        # let the exception be raised if it happens
        os.mkdir( samplenamedir )
        set_config_perms( samplenamedir )

    if os.path.exists( dst ):
        logging.warning( "%s already exists. Skipping" % dst )
    else:
        # Now symlink the file to the new destination
        logging.info( "Symlinking %s to %s" % (readfilepath, dst) )
        os.symlink( readfilepath, dst )

def get_platforms( ):
    return config['Platforms']

def get_datadirs( ):
    '''
        Only get directories for raw and read data
        ReadsBySample is not really a data dir
    '''
    dd = deepcopy( config['Paths']['DataDirs'] )
    del dd['READSBYSAMPLE_DIR']
    return dd

def create_directory_structure( ):
    '''
        Create the entire NGS directory structure
        using settings file
    '''
    create_ngs_dir()
    for name, path in get_datadirs().items():
        os.mkdir( path )
        set_config_perms( path )
        create_platform_dirs( path )
    rbs = config['Paths']['DataDirs']['READSBYSAMPLE_DIR']
    os.mkdir( rbs )
    set_config_perms( rbs )

def create_ngs_dir( ):
    '''
        Create NGS directory from settings file
    '''
    cdir = config['Paths']['NGSDATA_DIR']
    logging.info( "Creating NGS Data Dir {}".format( cdir ) )
    if os.path.isdir( cdir ):
        logging.info( "NGS Dir {} already exists".format( cdir ) )
        return
    os.mkdir( cdir )
    set_config_perms( cdir )

def create_platform_dirs( basepath ):
    '''
        Given a path and a sequence of platforms,
            create those directories inside of that path
    '''
    if not is_valid_abs_path( basepath ):
        raise ValueError( "{} is not a valid absolute path".format( basepath ) )
    platforms = get_platforms()
    for plat, path in platforms.items():
        logging.info( "Creating Platform directory {}".format( plat ) )
        os.mkdir( os.path.join( basepath, plat ) )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
