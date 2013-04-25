##################################################################
## Data directory structure library
##################################################################

import os
import os.path
import sys
import re
import logging

from wrairdata import settings
from wrairdata.util import *

def determine_platform_from_path( datapath ):
    '''
        Given a read data or raw data path extract the platform from it
        I.E: NGSData/ReadData/Sanger/2013_04_02 would return Sanger

        >>> dp = ['NGSData/ReadData/Sanger/2013_04_02', 'NGSData/ReadData/Roche454/2013_04_02', 'NGSData/ReadData/IonTorrent/2013_04_02', 'NGSData/ReadData/Bogus/2013_04_02', 'NGSData/RawData/Sanger/2013_04_02']
        >>> for d in dp:
        ...   try:
        ...     determine_platform_from_path( d )
        ...   except ValueError as e:
        ...     print "Caught"
        'Sanger'
        'Roche454'
        'IonTorrent'
        Caught
        'Sanger'
    '''
    platform_pat = "(" + "|".join( settings.PLATFORMS.keys() ) + ")"
    m = re.search( platform_pat, datapath )
    if m:
        return m.groups( 0 )[0]
    else:
        raise ValueError( "%s does not have a valid platform in it" % datapath )

def match_pattern_for_datadir( datadir ):
    ''' Determine platform from path then return key from dictionary '''
    platform = determine_platform_from_path( datadir )
    return settings.PLATFORMS[platform]['filename_match_pattern']

def link_reads_by_sample( datadir, outputbase ):
    '''
        Given an output directory with formatted read data
        Link all read files into the READSBYSAMPLE_DIR
        inside of the sample folder that they are for
    '''
    # Get platform to determine how to fetch read files
    platform = determine_platform_from_path( datadir )
    logging.debug( "Platform detected as: %s" % platform )
    # Fetch the correct pattern for the platform
    pattern = match_pattern_for_datadir( datadir )
    logging.debug( "File matching pattern: %s" % pattern )
    # Compile the match pattern
    cpattern = re.compile( pattern )

    if platform == 'Sanger':
        link_sanger_by_sample( datadir, outputbase, cpattern )
    else:
        link_sffreads_by_sample( datadir, outputbase, cpattern )

def link_sanger_by_sample( datadir, outputbase, cpattern ):
    # Loop through all sanger files
    for sf in get_all_( datadir, "*Sanger*" ):
        link_read_by_sample( sf, outputbase, cpattern )

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
        make_readonly( samplenamedir )

    if os.path.exists( dst ):
        logging.warning( "%s already exists. Skipping" % dst )
    else:
        # Now symlink the file to the new destination
        logging.info( "Symlinking %s to %s" % (readfilepath, dst) )
        os.symlink( readfilepath, dst )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
