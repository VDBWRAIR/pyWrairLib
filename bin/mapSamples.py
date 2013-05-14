#!/usr/bin/env python

##############################################################################
##  Author: Tyghe Vallard
##  Date: 3/21/2013
##  Email: vallardt@gmail.com
##  Purpose:
##      This script is intended to run gsMapper on all samples inside
##      of a Runfile.txt file that are not commented out.
##      It locates reads inside the directory set by readsbysampledir
##      It uses the sample name to locate the correct reads folder.
##      Right now it will only use .sff files as reads even though
##      gsmapper supports .fasta + .qual files as well.
##      The process that is performed is the same as the following commands:
##          newMapping -force <project directory>
##          setRef <project directory> <ref path in runfile>
##          for every sff file:
##              addRun <project directory> <sff read path>
##          joblist.append( runProject -vt <primer in runfile> -tr -trim -cpu 1 -bam -p <project_directory> )
##      Once all the samples have been added to the joblist the joblist is
##      executed in parallel using as many cpus as numCPU is set to
##      The generated gsMapper directories will be placed in the current directory
##      that the script is executed from.
##  Version:
##      - 1.0
##          Initial Script
##          project.
##  TODO:
##      - Somehow need to merge settings of this script and the wrairdata
##      - Logging needs to be easier to configure
##      - Currently logging only goes to a file and there is no indication
##          of the status of the mapping which is bad.
##############################################################################

import os
import os.path
import sys
import subprocess
from multiprocessing import Pool
import logging
from argparse import ArgumentParser

from wrairlib.runfiletitanium import RunFile
from wrairlib.util import get_all_

# Where is newbler installed
newbler_install_path = '/home/EIDRUdata/programs/newbler_v2.8/bin'

# How many CPUs to use
# Eidru has 24 so use 20 and leave some for other
# processes
numCPU=20

# The directory to search for read data for a sample
readsbysampledir="/home/EIDRUdata/NGSData/ReadsBySample"

# The log file to write to
logfile="mapSamples.log"

# Grab the logger
logging.basicConfig( level=logging.DEBUG, format='%(asctime)s -- %(name)s[%(levelname)s] -- %(message)s' )

logger = logging.getLogger( 'mapSamples' )
logger.info( "Starting up" )

class FailedCommand( Exception ):
    def __init__( self, msg ):
        self.msg = msg
        logging.critical( msg )
    def __str__( self ):
        return self.msg

def compileargs( *args, **kwargs ):
    arglist = []
    for k,v in kwargs.items():
        if isinstance( v, bool ) and v == True:
            arglist.append( '-%s' % k )
        else:
            arglist.append( '-%s %s' % (k,v) )
    return arglist

def runProjectParallel( kwargs ):
    projectdir = kwargs['projectdir']
    del kwargs['projectdir']
    return runProject( projectdir, **kwargs )

def runProject( projectdir, **kwargs ):
    ops = compileargs( **kwargs )
    logger.info( "Running project %s" % projectdir )
    cmd = [os.path.join( newbler_install_path, 'runProject')] + ops + [projectdir]
    retcode, output = run_newbler_cmd( cmd, projectdir )
    if retcode != 0:
        logger.critical( "Failed to run project %s. Error: %s" % (projectdir, output) )
    else:
        logger.info( output )

    return (projectdir, output, retcode)

def getSffsFromPath( path ):
    return [os.path.join( path, read ) for read in os.listdir( path ) if read[-4:] == '.sff']

def getSangersFromPath( path ):
    return get_all_( path, '*.fastq' )

def getReadsFromPath( path ):
    sffs = getSffsFromPath( path )
    sangers = getSangersFromPath( path )
    return sffs + sangers

def addRun( projectdir, readspath ):
    if os.path.isdir( readspath ):
        reads = getReadsFromPath( readspath )
    else:
        reads = [readspath]

    output = ""
    for read in reads:
        logger.info( "Adding read %s to project %s" % (read, projectdir) )
        cmd = [os.path.join( newbler_install_path, "addRun"), projectdir, read]
        retcode, output = run_newbler_cmd( cmd, projectdir )
        if retcode != 0:
            raise FailedCommand( "Failed to add read data from %s for %s" % (read, projectdir) )
        logger.info( "Added read %s to %s" % (read, projectdir) )

def setRef( projectdir, refpath ):
    cmd = [os.path.join( newbler_install_path, 'setRef' ), projectdir, refpath]
    logger.info( "Adding reference[s] %s to project %s" % (refpath, projectdir) )
    retcode, output = run_newbler_cmd( cmd, projectdir )
    if retcode != 0:
        raise FailedCommand( "Failed to add references for %s with error %s" % (projectdir, output) )
    logger.info( "Added references to %s" % projectdir )

def newMapping( projectdir, force=False ):
    if force == True:
        force = "-force "
    else:
        force = ""

    logger.info( "Creating new mapping project %s" % projectdir )
    cmd = [os.path.join( newbler_install_path, "newMapping" ), force, projectdir]
    retcode, output = run_newbler_cmd( cmd, projectdir )
    if retcode != 0:
        raise FailedCommand( "Failed to create project directory with error %s" % output )
    logger.info( "Created project %s" % projectdir )

def run_newbler_cmd( cmd, projectdir ):
    return run_cmd( cmd, cwd = os.path.dirname( os.path.abspath( projectdir ) ) )

def run_cmd( cmd, cwd ):
    # Open a new process for the command
    logger.info( "Running command:" )
    cmd = " ".join( cmd )
    logger.info( cmd )
    logger.info( "from within %s" % cwd )
    
    p = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd )
    # Wait for it to finish then return the stdout(which has stderr in it)
    output = p.communicate()[0]
    return (p.returncode, output)

def get_args( ):
    parser = ArgumentParser()

    parser.add_argument( '--runfile', dest='runfile', required=True, help = 'Runfile path to use' )

    args = parser.parse_args()
    if check_args( args ):
        return args
    sys.exit( -1 )

def check_args( args ):
    if os.path.exists( args.runfile ):
        return True
    return False

def main( ):
    args = get_args()


    runfile = args.runfile
    with open( runfile ) as fh:
        logger.debug( "Parsing Runfile %s" % runfile )
        rf = RunFile( fh )
        logger.info( "%d samples to map" % len( rf.samples ) )
        jobs = []
        failed_samples = []
        
        numSamples = len( rf.samples )

        # Try to maximize the cpu processing
        # if there are more samples than cpus, then just run each project with a single cpu
        p = None
        if numSamples >= numCPU:
            # Setup multiprocessing pool with numCpus
            processes = numCPU
            cpu_per_project = 1
            idlecpu = 0
        # If there are less samples than cpus, then run each sample with as many cpus as possible
        else:
            cpu_per_project, idlecpu = divmod( numCPU, numSamples )
            processes = int( numCPU / cpu_per_project )

        p = Pool( processes )
        logger.info( "Starting a Pool of %s workers" % numCPU )

        for sample in rf.samples:
            if not sample.disabled and sample.refgenomelocation:
                project_directory = "%s__%s__%s" % (sample.name, sample.midkeyname, sample.genotype)
                # If any of the commands fail, then bail on the sample don't try to run the project
                try:
                    newMapping( project_directory, force=True )
                    setRef( project_directory, sample.refgenomelocation )
                    addRun( project_directory, os.path.join( readsbysampledir, sample.name ) )
                except FailedCommand as e:
                    failed_samples.append( (sample.name, str(e)) )
                    logger.critical( "Leaving sample %s unmapped due to errors" % sample.name )
                    continue
                # Allocate idle cpu to project until none are left
                cpu = cpu_per_project
                if idlecpu > 0:
                    cpu += 1
                    idlecpu -= 1
                jobops = {'projectdir':project_directory, 'cpu': cpu, 'bam': True, 'numn': 0}
                # If the sample has primers listed then set them to be trimmed
                if sample.primers:
                    jobops.update( vt=sample.primers, tr=True, trim=True )
                jobs.append( jobops )
            else:
                logger.info( "Skipping %s because either commented out or missing reference path" % sample.name )

        for pdir, output, retcode in p.map( runProjectParallel, jobs ):
            if retcode != 0:
                failed_samples.append( (pdir, output) )

        for sample, err in failed_samples:
            logger.info( "%s failed due to %s" % (sample, err) )

if __name__ == '__main__':
    main()
