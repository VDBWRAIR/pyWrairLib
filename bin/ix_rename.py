#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os
import os.path
import sys
import re

from wrairlib.runfiletitanium import RunFile
from wrairdata import util
from wrairlib.settings import config, setup_logger

# Setup logger with script name
logger = setup_logger( name=os.path.basename(sys.argv[0]) )

def main( ):
    args = parse_args()
    sffpath = args.sffpath
    runfile = RunFile( args.runfile )
    region = args.region

    # Get sffs
    logger.info( "Starting the IonTorrent linking" )
    sfflist = glob( os.path.join( sffpath, 'IonXpress_*.sff' ) )
    logger.debug( "Sff files to link: {}".format(sfflist) )
    mapping = get_mapping( sfflist, runfile, region )
    logger.debug( "Mapping to use: {}".format(mapping) )
    path = create_readdir( runfile.date, runfile.platform )
    link_sffs( mapping, path )
    logger.info( "Finished linking" )

def link_sffs( mapping, path ):
    for src, dst in mapping.items():
        dst = os.path.join( path, dst )
        try:
            os.symlink( os.path.abspath(src), dst )
            logger.info( "Linking {} to {}".format(src,dst) )
        except OSError as e:
            logger.info( "{} already exists. Skipping".format( dst ) )
    
def create_readdir( date, platform ):
    date = date.strftime( '%Y_%m_%d' )
    path = os.path.join( config['Paths']['DataDirs']['READDATA_DIR'], platform, date )
    try:
        os.mkdir( path )
    except OSError as e:
        logger.debug( "{} already exists".format(path) )

    return path

def get_mapping( sfflist, runfile, region ):
    mapping = {}
    for sff in sfflist:
        #IonXpress_001_R_2012_09_05_15_55_31_user_VDB-26_2012_09_05.sff
        mid = re.search( 'IonXpress_(\d+)_.*', sff )
        if not mid:
            logger.error( "!!! Cannot obtain midkey from this filename: {}\n".format(sff) )
            logger.error( "!!! It will be skipped\n" )
            continue
        mid = mid.group( 1 )
        try:
            sample = runfile[int(region)]
        except KeyError:
            logger.critical( "Runfile does not have a region {}".format(region) )
            sys.exit( 1 )
        try:
            sample = sample['IX'+mid]
        except KeyError:
            logger.error( 
                "Runfile does not contain an entry for {} for region {}. It will be skipped".format(
                    os.path.basename(sff), region
                )
            )
            continue
        newname = util.demultiplex_sample_name( sample, runfile.platform )
        mapping[sff] = newname
    return mapping

def parse_args( ):
    parser = ArgumentParser()

    parser.add_argument( dest='sffpath', help='Path to SFFCreator_out dir' )
    parser.add_argument( dest='runfile', help='Runfile path' )
    parser.add_argument( dest='region', help='Region this run is for' )

    return parser.parse_args()

if __name__ == '__main__':
    main()
