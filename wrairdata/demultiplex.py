import os
import os.path
import sys

from util import *

def demultiplex( runfilepath, sffdir, outputdir=os.getcwd(), midparsefile='/opt/454/config/MidConfig.parse', sfffilecmd='/opt/454/bin/sfffile' ):
    '''
        Given a runfilepath and a sffdir path
        Demultiplex the all the sff files inside of sffdir
        Place them in outputdir or in current directory if not provided

        Name each sff file outputed using the sample name from the runfile that matches the mid for the sample

        Follows VDB_Sample_naming_Standards

        >>> if os.path.exists( 'testoutput' ):
        ...     shutil.rmtree( 'testoutput' )
        >>> fp = '/home/EIDRUdata/NGSData/ReadData/Roche454/D_2013_03_13_13_56_26_vnode_signalProcessing'
        >>> demultiplex( fp + '/meta/Runfile__FlxPlus__2013_03_12.txt', fp + '/sff', 'testoutput', '/home/EIDRUdata/NGSData/MidParse.conf' ) 
    '''
    # Make outputdir if not exists
    if not os.path.exists( outputdir ):
        logging.info( "Creating output directory %s" % outputdir )
        os.makedirs( outputdir )
        make_readonly( outputdir )

    # Get the sff files indexed by their number
    sff_files = get_sff_files( sffdir )

    # Try to open the runfile
    try:
        with open( runfilepath ) as fh:
            # Run file instance
            rf = RunFile( fh )
            sffprocesses = []
            # Make output region directories
            for region in rf.regions:
                # Make region output directory if it doesn't exist
                region_dir = os.path.join( outputdir, str( region ) ) 
                if not os.path.exists( region_dir ):
                    logging.info( "Creating region output directory %s" % region_dir )
                    os.mkdir( region_dir )
                    make_readonly( region_dir )
                else:
                    logging.info( "Region output directory %s already exists" % region_dir )
                # Demultiplex the sff file into that directory
                p = demultiplex_sff( sff_files[region], midparsefile, sfffilecmd, os.path.join( outputdir, str( region ) ) )
                # Keep track of our opened process and what sff file it is demultiplexing
                sffprocesses.append( (p,sff_files[region]) )

            # Should wait for both processes to finish
            failed = False
            for p, sfffile in sffprocesses:
                stdout, stderr = p.communicate()
                logging.info( stdout )
                if stderr.strip():
                    logging.error( '%s' % stderr )
                    failed = True

            if failed:
                sys.stderr.write( "Some sff files faile to demultiplex. Check log file.\n" )
                sys.exit( -1 )
            else:
                make_readonly_recursive( outputdir )
                logging.info( "Demultiplex completed" )
    except IOError as e:
        sys.stderr.write( "Got %s while trying to open %s\n" % (runfilepath, e) )
        logging.error( "Got %s while trying to open %s\n" % (runfilepath, e) )

def demultiplex_sff( sfffile, midparsefile, sfffilecmd, outputdir=os.getcwd() ):
    '''
        Run
        cd outputdir
        sfffile -mcf midparsefile -s sfffilepath
    '''
    cmdline = sfffilecmd.split() + ['-mcf', midparsefile, '-s', sfffile]
    logging.info( "Running %s" % " ".join( cmdline ) )
    p = subprocess.Popen( cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=outputdir )
    return p

def rename_demultiplexed_sffs( outputdir, runfile ):
    '''
        Given an output directory from running demultiplex and a runfile
        Rename all of the generated sff files using rename_sample_sff
        so they have a more useful name
    '''
    # Get all the sff files inside of the main output directory
    all_sff = get_all_sff( outputdir )
    logging.debug( "All sff files found inside of %s:\n%s" % (outputdir, all_sff) )
    sff_mapping = runfile_to_sfffile_mapping( runfile )
    logging.debug( "Mapping for sff file names:\n%s" % sff_mapping )
    rf = RunFile( open( runfile ) )
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
