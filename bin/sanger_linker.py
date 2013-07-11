#!/usr/bin/env python

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
        >>> assert nn == 'H01_325__R8237__Sanger__2013_07_10__Den2.ab1', nn
    '''
    # Remove the well from the string
    well_re = '_[A-H][0-9]{2}(?=\.ab1)'
    sf = re.sub( well_re, '', sangerfile )

    # Parse the filename
    f = Formatter( config['Platforms'] ).Sanger
    pat = f.rawread_format.input_format
    m = pat.match( sf )
    if not m:
        logger.error( "{} does not seem to be a valid sanger raw read name.".format(sf) )
        logger.debug( "Could not match against {}".format( pat.pattern ) )
        raise ValueError( "{} not a valid sanger name".format( sf ) )

    return f.rawread_format.output_format.format( **m.groupdict() )

def sanger_date( sangerdir ):
    '''
        Parse sangerdir basename to get the finish date out of it
        
        @param sangerdir - Something like Run_3130xl_2013-07-10_17-56_1032_2013-07-10
        @return date string

        >>> dt = sanger_date( 'Run_3130xl_2013-07-10_17-56_1032_2013-07-10' )
        >>> assert dt == '2013_07_10', dt
    '''
    return sangerdir[-10:].replace( '-', '_' )

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
    dst = rename_sanger_file( basename( sfile ) )
    readdatadir = config['Paths']['DataDirs']['READDATA_DIR']
    readdatadir = join( readdatadir, 'Sanger', dt )
    return join( readdatadir, dst )

def linkrename( sangerfiles ):
    '''
        Rename and link all files inside of sangerfiles

        @param sangerfiles - List of sanger file paths
    '''

    logger.debug( "Files to rename: {}".format( sangerfiles ) )
    for sfile in sangerfiles:
        sfile = os.path.abspath( sfile )
        try:
            dst = get_dst( sfile )
        except ValueError:
            logger.error( "Ruh row raggie! Could not get destination for {}".format(sfile) )
            continue

        if os.path.exists( dst ):
            linkpath = os.readlink( dst )
            if dirname( linkpath ) != dirname( sfile ):
                logger.error( "Destination({}) for {} already exists".format(
                    dst, sfile)
                )
            logger.info( "{} will be skipped as it already exists".format(sfile) )
            continue
        else:
            os.symlink( sfile, dst )
            logger.info( "Linked {}".format( sfile ) )
            logger.debug( "Linked {} to {}".format( sfile, dst ) )

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
