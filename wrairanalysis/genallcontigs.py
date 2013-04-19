#!/usr/bin/env python

##############################################################################
##  Author: Tyghe Vallard
##  Date: 3/21/2013
##  Email: vallardt@gmail.com
##  Purpose:
##      Searches inside a given directory for any gsMapper directories
##      For every gsMapper directory found, runs to_allsamples from
##      allcontig_to_allsample.py script
##      From the records returned(fastq records) writes them to a file
##      named after the project directory inside of the given output
##      directory.
##      The output is essentially a single directory containing
##      Merged 454AllContigs.fna & .qual files into a .fastq file
##      for each gsMapper directory
##  Version:
##      1.0 -
##          Initial Script
##############################################################################

from argparse import ArgumentParser
import sys
import os
import os.path
import re

from allcontig_to_allsample import to_allsample
from wrairlib.fff.fffprojectdir import get_sample_from_dir_path

# Setup logger
import logging
logger = logging.getLogger( 'test' )

def setup_logger( level ):
    logger.setLevel( getattr( logging, level ) )
    soh = logging.StreamHandler( )
    soh.setLevel( getattr( logging, level ) )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    soh.setFormatter(formatter)
    logger.addHandler( soh )

def get_output_dir( maindir, outdir ):
    if not outdir:
        outdir = 'FastaContigs'
    outdir = os.path.join( maindir, outdir )
    logger.debug( "Output directory: %s" % outdir )
    # Make sure the directory exists
    if not os.path.exists( outdir ):
        logger.debug( "%s did not exist. Creating" % outdir )
        os.mkdir( outdir )

    return outdir

def is_gsdir( path ):
    # Has to be a directory and contain 454Project.xml
    logger.debug( "Checking to see if %s is a gs directory" % path )
    isgsdir = os.path.isdir( path ) and os.path.exists( os.path.join( path, '454Project.xml' ) )
    logger.debug( "Result: %s" % isgsdir )
    return isgsdir

def get_gsdirs( maindir ):
    return [os.path.join( maindir, d ) for d in os.listdir( maindir ) if is_gsdir( os.path.join( maindir, d ) )]

def contig_to_sample( gsdir, outputdir ):
    logger.info( "Processing %s" % gsdir )
    outfile = os.path.join( outputdir, "%s.fastq" % os.path.basename( gsdir ) )
    with open( outfile, 'w' ) as ofh:
        records_written = to_allsample( gsdir, ofh )
    logger.info( "%d sequences written to %s" % (records_written, outfile) )

def main( args ):
    setup_logger( args.loglevel )
    # Ensure directory exists and gets default value
    outdir = get_output_dir( args.maindir, args.outdir )
    logger.info( "Generating %s" % outdir )
    for gsdir in get_gsdirs( args.maindir ):
        contig_to_sample( gsdir, outdir )

def get_args( ):
    parser = ArgumentParser()

    parser.add_argument( '-d', dest='maindir', required=True, help='Top directory containing multiple gs project directories' )
    parser.add_argument( '-o', '--out-dir', dest='outdir', default=None, help='Ouput directory[Default: FastaContigs inside of directory specified with -d option' )
    parser.add_argument( '-l', '--log-level', dest='loglevel', default='INFO', choices=('DEBUG','INFO'), help='What logging level to use[Default: INFO]')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main( get_args() )
