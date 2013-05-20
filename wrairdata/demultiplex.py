import os
import os.path
import sys
from StringIO import StringIO
import re

from util import *

class ReadList( object ):
    ''' Read the output of sfffile -s '''
    @classmethod
    def _open( self, fh_fp ):
        if isinstance( fh_fp, str ):
            return open( fh_fp )
        else:
            return fh_fp

    @classmethod
    def parse( self, fh_fp ):
        fh = ReadList._open( fh_fp )
        cpat = re.compile( '^(?P<barcode>\S+):\s+(?P<numreads>\d+)\s+reads .*$' )
        reads = {}
        for line in fh:
            line = line.strip()
            m = cpat.match( line )
            if m:
                read = m.groupdict()
                reads[read['barcode']] = read['numreads']
        return reads

def demultiplex( sffdir, outputdir, midparsefile, sfffilecmd ):
    '''
        Given a sffdir path
        Demultiplex the all the sff files inside of sffdir
        Place them in outputdir or in current directory if not provided

        Ensures outputdir exists(will create dirs all the way to it like mkdir -p)
        Ensures sffdir is valid

        Creates a directory for each sfffile region(last 2 digits before .sff in each sfffile)

        Returns dictionary keyed by each sfffile's name with a value of another dictionary
            that is keyed by the barcode outputted by the command with value of how many reads were written
            for that barcode
    '''
    # ensures sffdir is abspath
    sffdir = abspath_or_error( sffdir )

    # Get the sff files indexed by their number
    sff_files = get_sff_files( sffdir )

    if len( sff_files ) == 0:
        logging.warning( "No sff files to demultiplex in {}".format(sffdir) )
        return

    # Make outputdir if not exists
    if not os.path.exists( outputdir ):
        logging.info( "Creating demultiplexed sff output directory {}".format(outputdir) )
        os.makedirs( outputdir )
        set_config_perms( outputdir )

    # Loop through every region's sff files
    sffprocesses = []
    for region, sffpath in sff_files.items():
        # Make region output directory if it doesn't exist
        region_dir = os.path.join( outputdir, str( region ) ) 
        if not os.path.exists( region_dir ):
            logging.info( "Creating region output directory {}".format(region_dir) )
            os.mkdir( region_dir )
            set_config_perms( region_dir )
        else:
            logging.info( "Region output directory %s already exists" % region_dir )

        # Demultiplex the sff file into that directory
        p = demultiplex_sff( sff_files[region], midparsefile, sfffilecmd, os.path.join( outputdir, str( region ) ) )
        # Keep track of our opened process and what sff file it is demultiplexing
        sffprocesses.append( (p,sff_files[region]) )

    # Should wait for both processes to finish
    failed = False
    results = {}
    for p, sfffile in sffprocesses:
        stdout, stderr = p.communicate()
        logging.info( stdout )
        if stderr.strip():
            logging.error( "{} failed to demultiplex with error: {}".format(sfffile, stderr) )
            failed = True
        else:
            print sfffile
            results[os.path.basename(sfffile)] = ReadList.parse( StringIO(stdout) )

    if not failed:
        set_config_perms_recursive( outputdir )
        logging.info( "Demultiplex completed" )
        return results
    else:
        return {}

def demultiplex_sff( sfffile, midparsefile, sfffilecmd, outputdir ):
    '''
        sfffile - Actual sfffile to demultiplex
        midparsefile - Config file mapping barcodes to barcode sequences
        sfffilecmd - Path to sfffile command line utility
        outputdir - Directory path to output sfffile command output

        Same as running:
        cd outputdir
        sfffile -mcf midparsefile sfffilepath
    '''
    cmdline = sfffilecmd.split() + ['-mcf', midparsefile, '-s', sfffile]
    logging.debug( "Running %s" % " ".join( cmdline ) )
    p = subprocess.Popen( cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=outputdir )
    return p

def rename_demultiplexed_sffs( demultiplexed_dir, runfile ):
    '''
        Given an output directory from running demultiplex and a runfile(demultiplexed_dir)
         rename all of the demultiplexed files so that they conform to the naming standard in the
         settings

        Ensure demultiplexed_dir exists and is not empty
        Ensure demultiplexed_dir contains regions(numerical dirs 1,2,3...) with demultiplexed reads(454Reads.<barcode>.sff)
        Ensure runfile exists and is readable
    '''
    # Get all the sff files inside of the main output directory
    rf = RunFile( open( runfile ) )
    all_sff = get_all_sff( demultiplexed_dir )
    logging.debug( "All sff files found inside of %s:\n%s" % (demultiplexed_dir, all_sff) )
    sff_mapping = runfile_to_sfffile_mapping( rf )
    logging.debug( "Mapping for sff file names:\n%s" % sff_mapping )
    # Loop through each region
    for region, sffs in all_sff.items():
        # Loop through every sfffile
        for sfffile in sffs:
            filename = os.path.basename( sfffile )
            outdir = os.path.dirname( sfffile )
            # Try to get the filename key from the mapping
            newfilename = sff_mapping[region].get( filename, False )

            # If there was a mapping name
            if newfilename:
                logging.debug( "Filename: %s -- Directory Containing Filename: %s -- New Filename: %s" % 
                    ( filename, outdir, newfilename)
                )
                newname = os.path.join( outdir, newfilename )
                if os.path.lexists( newname ):
                    logging.info( "Removing existing sff file %s" % newname )
                    os.unlink( newname )
                logging.info( "Linking %s to %s" % (sfffile, newname) )
                os.rename( sfffile, newname )
            # The runfile is incorrect if there is no mapping for
            # an sff file generated
            else:
                logging.error( "No mapping key found for %s. Are all samples in the runfile?" % filename )
