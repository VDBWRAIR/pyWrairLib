##################################################################
## Data directory structure library
##################################################################

import os
import os.path
import sys
import re
from glob import glob
from copy import deepcopy

from wrairlib.settings import config, setup_logger
from util import *

logger = setup_logger( name=__name__ )

def determine_platform_from_path( datapath ):
    '''
        Given a read data or raw data path extract the platform from it
        I.E: NGSData/ReadData/Sanger/2013_04_02 would return Sanger
        
        Resolves symlinks

        @param datapath - Path to a file
        @return platform datapath belongs to or ValueError
    '''
    if os.path.islink( datapath ):
        abs_datapath = os.readlink( datapath )
    else:
        abs_datapath = os.path.abspath( datapath )
    platform_pat = "(" + "|".join( get_platforms().keys() ) + ")"
    m = re.search( platform_pat, abs_datapath )
    if m:
        platform = m.groups(0)[0]
        logger.debug( "Platform detected as: %s" % platform )
        return platform
    else:
        raise ValueError( "%s does not have a valid platform in it" % datapath )

def match_pattern_for_datadir( datadir ):
    ''' Determine platform from path then return key from dictionary '''
    platform = determine_platform_from_path( datadir )
    pattern = config['Platforms'][platform]['read_in_format']
    logger.debug( "Using file matching pattern: %s" % pattern )
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

    logger.debug( "Linking Reads from {} into {}".format( datadir, outputbase ) )
    # Get platform to determine how to fetch read files
    platform = determine_platform_from_path( datadir )
    # Fetch the correct pattern for the platform
    pattern = match_pattern_for_datadir( datadir )
    # Compile the match pattern
    cpattern = re.compile( pattern )

    # Walk the dir structure
    for root, dirs, files in os.walk( datadir ):
        for read in files:
                link_read_by_sample( os.path.join( root, read ), outputbase, cpattern )

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
    readfilepath = abspath_or_error( readfilepath )

    # Get just the basename of the filepath
    readfile = os.path.basename( readfilepath )

    # Attempt the file pattern match
    m = matchpattern.match( readfile )
    if m is None:
        logger.warning( "Name scheme used: {}".format( matchpattern.pattern ) )
        logger.warning( "Read file %s does not conform to the naming scheme in settings file." % readfile )
        logger.warning( "It will be skipped" )
        return

    # Get the file info from the name of the file
    fileinfo = m.groupdict()
    logger.debug( "Filename info: %s" % fileinfo )

    # The path to the symlink
    # <outputbase>/<samplename>/<orig filename>
    samplenamedir = os.path.join( outputbase, fileinfo['samplename'] )
    dst = os.path.join( samplenamedir, readfile )
    logger.debug( "Destination for symlink: %s" % dst )

    # Make sure samplenamedir exists
    if not os.path.exists( samplenamedir ):
        logger.info( "Creating samplename directory %s" % samplenamedir )
        # let the exception be raised if it happens
        os.mkdir( samplenamedir )
        set_config_perms( samplenamedir )

    if os.path.islink( dst ):
        logger.warning( "%s already exists. Skipping" % dst )
    else:
        # Now symlink the file to the new destination
        logger.info( "Symlinking %s to %s" % (readfilepath, dst) )
        try:
            os.symlink( readfilepath, dst )
        except OSError as e:
            logger.critical( "Somehow {} already exists even though I checked for it" )

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
        try:
            os.mkdir( path )
        except OSError as e:
            if e.errno == 17:
                logger.info( "{} already exists.".format(path) )
                continue
            else:
                logger.exception( "Unkown error occurred trying to create {}".format(path) )
                raise e
        set_config_perms( path )
        create_platform_dirs( path )
    rbs = config['Paths']['DataDirs']['READSBYSAMPLE_DIR']
    try:
        os.mkdir( rbs )
        set_config_perms( rbs )
    except OSError as e:
        if e.errno == 17:
            logger.info( "{} already exists.".format(rbs) )
            return
        else:
            logger.exception( "Unkown error occurred trying to create {}".format(rbs) )
            raise e

def create_ngs_dir( ):
    '''
        Create NGS directory from settings file
    '''
    cdir = config['Paths']['NGSDATA_DIR']
    logger.info( "Creating NGS Data Dir {}".format( cdir ) )
    if os.path.isdir( cdir ):
        logger.info( "NGS Dir {} already exists".format( cdir ) )
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
        logger.info( "Creating Platform directory {}".format( plat ) )
        tpath = os.path.join( basepath, plat )
        try:
            os.mkdir( tpath )
        except OSError as e:
            if e.errno == 17:
                logger.info( "{} already exists.".format( tpath ) )
                continue
            else:
                logger.exception( "Unkown error occurred trying to create {}".format(tpath) )
                raise e

def filter_reads_by_platform( reads, platform_include=[] ):
    '''
        Filter reads based on given platform.

        @param reads - List of read paths
        @param platform_include - List of platform's to include reads for
        
        @return a list of reads for platforms in platform_include
    '''
    if len( platform_include ) == 0 or len( reads ) == 0:
        return reads

    reads_keep = []
    for i in range( len( reads ) ):
        keep = False
        for plat in platform_include:
            # Only keep reads that match pattern for platform
            if determine_platform_from_path( reads[i] ) == plat:
                keep = True
                reads_keep.append( reads[i] )
        if not keep:
            logging.debug( "Filtering out read {}".format(reads[i]) )

    return reads_keep

if __name__ == '__main__':
    import doctest
    doctest.testmod()
