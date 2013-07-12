#!/usr/bin/env python
import pdb
import re
from glob import glob
from argparse import ArgumentParser
import os
import os.path
import sys
from os.path import basename, dirname, join

from wrairnaming import Formatter
from wrairlib.settings import config, setup_logger

# Setup the logger
logger = setup_logger( name=basename( sys.argv[0] ) )

def rename_sanger_file( sangerfile ):
    '''
        Inserts an additional underscore between each set of information
        Removes well information off the end
        
        @param sangerfile - Something like H01_325_R8237_Sanger_2013_07_10_Den2_B04.ab1
        @return Same file but with 2x underscores separating pieces of info. Also
            chops off the Well info at the end.

        >>> nn = rename_sanger_file( 'H01_325_R8237_Sanger_2013_07_10_Den2_B04.ab1' )
        >>> assert nn == 'H01_325__R8237__Sanger__2013_07_10__Den2__None__None.ab1', nn
        >>> nn = rename_sanger_file( 'H01_325_R8237_Sanger_2013_07_10_Den2_0001.ab1' )
        >>> assert nn == 'H01_325__R8237__Sanger__2013_07_10__Den2__None__0001.ab1', nn
    '''
    # Work with only the basename
    sf = basename( sangerfile )

    # Remove the well from the string
    well_re = '_[A-H][0-9]{2}(?=\.ab1)'
    sf = re.sub( well_re, '', sf )
    logger.debug( "Using {} as name".format( sf ) )


    # Parse the filename
    f = Formatter( config['Platforms'] ).Sanger
    pat = f.rawread_format.input_format
    m = pat.match( sf )
    if not m:
        pdb.set_trace()
        logger.error( "{} does not seem to be a valid sanger raw read name.".format(sf) )
        logger.debug( "Could not match against {}".format( pat.pattern ) )
        raise ValueError( "{} not a valid sanger name".format( sf ) )

    pieces = m.groupdict()
    logger.debug( "Parsed file pieces: {}".format( pieces ) )
    # If the filename doesn't have the runnum, get it from the directory
    if 'runnum' not in pieces or pieces['runnum'] in ('None',None):
        sangerdir = basename( dirname( sangerfile ) )
        # If an abspath was not given then we can't get info from sangerdir
        if sangerdir.replace( ' ', '' ) != '':
            pieces['runnum'] = parse_sangerrundir( sangerdir )['runnum']
            logger.debug('Appending runnum {} from directory {} ' \
                'as it did not exist in file'.format(pieces['runnum'],sangerdir))

    logger.debug( "Using {} to fill in output format {}".format(
        pieces, f.rawread_format.output_format ))
    return f.rawread_format.output_format.format( **pieces )

def sanger_date( sangerdir ):
    '''
        Parse sangerdir basename to get the finish date out of it
        
        @param sangerdir - Something like Run_3130xl_2013-07-10_17-56_1032_2013-07-10
        @return date string

        >>> dt = sanger_date( 'Run_3130xl_2013-07-10_17-56_1032_2013-07-10' )
        >>> assert dt == '2013_07_10', dt
    '''
    return parse_sangerrundir( sangerdir )['enddate'].replace( '-', '_' )

def ensure_sangerdate( date ):
    '''
        Utility function to ensure that the ReadData/Sanger/<date> directory exists

        @param date - YYYY_MM_DD formatted date string
    '''
    readdatadir = config['Paths']['DataDirs']['READDATA_DIR']
    readdatadir = join( readdatadir, 'Sanger', date )

    if not re.match( '\d{4}_\d{2}_\d{2}', date ):
        raise ValueError( "{} is not of format YYYY_MM_DD".format( date ) )

    # check already exists
    if os.path.isdir( readdatadir ):
        return

    # Try to create dir
    try:
        os.mkdir( readdatadir )
        logger.info( "Created {}".format( readdatadir ) )
    except OSError:
        logger.critical( "Could not create {}".format( readdatadir ) )
        sys.exit( -1 )

def get_dst( sfile ):
    dt = sanger_date( basename( dirname( sfile ) ) )
    ensure_sangerdate( dt )
    dst = rename_sanger_file( sfile )
    readdatadir = config['Paths']['DataDirs']['READDATA_DIR']
    readdatadir = join( readdatadir, 'Sanger', dt )
    return join( readdatadir, dst )

def parse_sangerrundir( dirpath ):
    '''
        Parses a sanger run directory
        @param dirpath - Something like Run_3130xl_2013-07-09_17-39_1030_2013-07-10
        @return dictionary of pieces 

        >>> rundir = 'Run_3130xl_2013-07-09_17-39_1030_2013-07-10'
        >>> pieces = parse_sangerrundir( rundir )
        >>> assert pieces == { \
                'machinename': '3130xl', 'startdate': '2013-07-09', \
                'enddate': '2013-07-10', 'runnum': '1030' \
             }, pieces
    '''
    # Get only the directory's basepath
    dp = basename( dirpath )

    f = Formatter( config['Platforms'] ).Sanger
    pat = f.rawdir_format.input_format
    m = pat.match( dp )

    if not m:
        raise ValueError( "Sanger directory {} is not parsable by the " \
            "rawdir_in_format in settings file".format( dp ) )

    return m.groupdict()

def rename( sfile ):
    '''
        Rename and link a single sanger file
        @parm sangerfile path
    '''
    sfile = os.path.abspath( sfile )
    try:
        dst = get_dst( sfile )
    except ValueError as e:
        logger.error( "Ruh row raggie! Could not get destination for {}".format(sfile) )
        logger.debug( "Error was {}".format( e ) )
        return

    # If the the destination exists, we must investigate why
    if os.path.exists( dst ):
        # Where does the destination's link point to
        linkpath = os.readlink( dst )
        # If the destination's link directory does not match this 
        # file's directory then we assume the two files are not the same file
        # which means the naming scheme is not unique and the name needs to be
        # modified
        if dirname( linkpath ) != dirname( sfile ):
            logger.warning( "{} is not a unique name and already exists in " \
                "destination {}".format( sfile, dst))
            logger.warning( "It will be skipped. See logfile for more info." )
        else:
            logger.info( "Skipping {} as it already exists in destination".format(
                sfile ))
        # Stop here since the file already exists. The user will have to figure
        # it out
        return
    os.symlink( sfile, dst )
    logger.info( "Linked {}".format( sfile ) )
    logger.debug( "Linked {} to {}".format( sfile, dst ) )

def linkrename( sangerfiles ):
    '''
        Rename and link all files inside of sangerfiles

        @param sangerfiles - List of sanger file paths
    '''

    logger.debug( "Files to rename: {}".format( sangerfiles ) )
    for sfile in sangerfiles:
        rename( sfile )

def parse_args( ):
    parser = ArgumentParser()

    parser.add_argument( dest='sangerfiles', help='Directory of sanger files' )

    return parser.parse_args()

def main( ):
    args = parse_args()

    logger.info( "Starting sanger renaming" )
    linkrename( glob( join( args.sangerfiles, '*.ab1' ) ) )
    logger.info( "Finished renaming" )

if __name__ == '__main__':
    main()
