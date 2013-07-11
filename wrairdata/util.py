import os
import os.path
import sys
from glob import glob
import shutil
import subprocess
import datetime
import logging
import fnmatch
import re

from wrairlib.runfiletitanium import RunFile, RunFileSample
from wrairnaming import Formatter

from wrairlib.settings import config, setup_logger
logger = setup_logger( name=__name__ )

def is_valid_abs_path( path, pType='dir' ):
    '''
        Ensure path is absolute, valid and is pType
        pType should be dir, link or file
    '''
    valid_ptype = ('dir','link','file')
    ptype = pType.lower()

    if ptype not in valid_ptype:
        raise ValueError( '{} not in {}'.format(pType,valid_ptype) )

    if not os.path.isabs( path ):
        return False

    return getattr( os.path, 'is' + ptype )( path )

def abspath_or_error( path ):
    ''' Convert to abs path and verify it or throw ValueError '''
    path = os.path.abspath( path )
    try:
        os.stat( path )
    except OSError as e:
        raise ValueError( "{} is not a valid abs path({})".format(path,e) )
    return path

def get_all_( datadir, fmatch ):
    '''
        Get all files matching fmatch in datadir
        Ensures datadir is a valid absolute path
    '''
    # Ensure path is abs
    datadir = abspath_or_error( datadir )
    logger.debug( "Getting all {} inside of {}".format(fmatch, datadir) )
    files = glob( os.path.join( datadir, fmatch ) )
    logger.debug( "Found files: %s" % files )
    return files

def get_multiplexed_sffs( sdir ):
    '''
        Return all region multiplexed sff files from sdir
        Returns only all uppercase and that have 2 digit preceding .sff
        abs paths returned
    '''
    sdir = abspath_or_error( sdir )
    sffs = get_all_( sdir, '*.sff' )
    rsffs = []
    for sff in sffs:
        name,ext = os.path.splitext( os.path.basename( sff ) )
        # Skip names that are not all uppercase
        if name.upper() != name:
            logger.debug( "Skipping {} because it is not completely uppercase".format( name ) )
            continue
        # Skip names that do not have 2 digits at the end
        try:
            int( name[-2:] )
        except ValueError:
            logger.debug( "Skipping {} because it does not contain a valid region number before the .sff".format(name) )
            continue
        rsffs.append( sff )
    return rsffs

def get_sff_files( sffdir ):
    '''
        Return all multiplexed sff files in sffdir that are all Uppercase and have 2 digits preceding .sff
        Returns a dictionary keyed by the 2 digits(converted to int so might only be 1 digit) and the values are the paths to the sff files

        Typically these are 454 SFF files from signal processing and represent a region each
    '''
    # The list of sff files
    sffs = get_multiplexed_sffs( sffdir )
    sff_files = {}
    for sff in sffs:
        name,ext = os.path.splitext( os.path.basename( sff ) )
        try:
            reg = int( name[-2:] )
        except ValueError as e:
            logger.critical( "{} cannot be parsed into a region integer".format( reg ) )
            raise ValueError( "Ruhh Rohh Raggie. {} should not have been raised here".format( e ) )
        if reg in sff_files:
            logger.critical( "Compiled sff list so far {}".format( sff_files ) )
            logger.critical( "Sff file that is throwing the exception: {}".format( sff ) )
            raise ValueError( "There are more than 1 sff files for region {}.".format( reg ) )
        sff_files[reg] = sff
    return sff_files

def get_all_sff( outputdir ):
    '''
        Given an output directory from running demultiplex
        Get all the sff files from that directory
        split up into sub lists of regions
    '''
    sff_files = {}
    outputdir = abspath_or_error( outputdir )
    for rdir in os.listdir( outputdir ):
        if os.path.isdir( os.path.join( outputdir, rdir ) ):
            logger.debug( "Compiling Region %s SFF files list" % rdir )
            region_sffs = []
            for sff in get_all_( os.path.join( outputdir, rdir ), '*.sff' ):
                region_sffs.append( sff )
            sff_files[int(rdir)] = region_sffs
    return sff_files

def rename_sample_sff( sfffile, sample ):
    '''
        Rename a sfffile sample
        given the demultiplexed sff file and sample instance for that file
    '''
    outdir = os.path.dirname( sfffile )
    filename = demultiplex_sample_name( sample )
    newnamepath = os.path.join( outdir, filename )
    return newnamepath

def runfile_to_sfffile_mapping( runfile ):
    '''
        Return a dictionary that will be useful to map a demultiplexed
        sff file name to it's new sample name
        sfffile -s splits into files with the following name pattern:
            454Reads.<mid>.sff
    '''
    if isinstance( runfile, str ):
        # Parse the runfile
        rf = RunFile( open( runfile ) )
    else:
        rf = runfile
    # Start the mapping with just the regions split out
    mapping = {region:{} for region in rf.regions}
    f = Formatter( config['Platforms'] )
    f = getattr( f, runfile.platform )
    # Root key should be by region
    for sample in rf.samples:
        readname = f.rawread_format.output_format.format( midkey=sample.midkeyname )
        mapping[sample.region][readname] = demultiplex_sample_name( sample, rf.platform )
    
    return mapping

def demultiplex_sample_name( sample, platform ):
    r'''
        Return a demultiplexed sff file name from a given RunFileSample instance
    '''
    f = Formatter( config['Platforms'] )
    f = getattr( f, platform )
    return f.read_format.get_output_name(
        samplename=sample.name,
		midkey=sample.midkeyname,
		date=sample.date.strftime( '%Y_%m_%d' ),
		virus=sample.genotype,
        region=sample.region,
		extension='sff'
    )

def exec_recursive( path, func, *args, **kwargs ):
    '''
        Execute func recursively on every file and directory inside of path
    '''
    all_ret = []
    for root, dirs, files in os.walk( path ):
        all_ret += [func( os.path.join( root, fd ), *args, **kwargs ) for fd in dirs]
        all_ret += [func( os.path.join( root, fd ), *args, **kwargs ) for fd in files]
    return all_ret

def set_config_perms( path ):
    '''
        Change perms to what settings are set to
    '''
    g = config['DEFAULT']['Group']
    p = config['DEFAULT']['Perms']

    fail_flag = False

    try:
        group = int( g )
    except ValueError as e:
        logging.warning( "Group value({}) in config is not a valid integer value".format( g ) )
        fail_flag = True

    try:
        perms = int( p, 8 )
    except ValueError as e:
        logging.warning( "Perms value({}) in config is not a valid Octal integer value".format( p ) )
        fail_flag = True

    if fail_flag:
        logging.warning( "Not attempting to set permissions on {} because of above errors".format( path ) )
        return False

    return set_perms( path, perms, group )

def set_config_perms_recursive( path ):
    set_config_perms( path )
    exec_recursive( path, make_readonly )
    
def make_readonly( path ):
    '''
        Refactored set_config_perms
    '''
    set_config_perms( path )

def make_readonly_recursive( rootpath ):
    set_config_perms_recursive( rootpath )

def set_perms( path, perms, gid=os.getgid(), recursive=False ):
    '''
        Sets permissions, uid, gid on a path
    '''
    succeeded = True
    if not os.path.isabs( path ):
        raise ValueError( "{} is not a valid abs path".format(path) )

    if not isinstance( gid, int ):
        gid = int( gid )

    if not isinstance( perms, int ):
        perms = int( perms, 8 )
        
    try:
        logger.debug( "Changed permissions of %s to %s" % (path, perms) )
        os.chmod( path, perms )
    except OSError as e:
        succeeded = False
        logger.warning( str(e) )

    try:
        logger.debug( "Changed gid of %s to %s" % (path, gid) )
        os.chown( path, os.getuid(), gid )
    except OSError as e:
        succeeded = False
        logger.warning( "{}: Are you in group {}?".format(str(e),gid) )

    if recursive:
        return all( exec_recursive( path, set_perms, perms, gid ) )
    else:
        return succeeded

def set_perms_recursive( path, perms, gid=os.getgid() ):
    make_readonly_recursive( path )

def date_from_path( path ):
    '''
        Get the run date from a path

        @param path - Directory path probably pointing to SFFCreator_out. Should
            contain a run date in it.(Easiest to supply abspath)
        @return date string YYYY_MM_DD of the found date in the path
    '''
    # Ensure abs path
    path = os.path.abspath( path )
    m = re.search( '\d{4}_\d{2}_\d{2}', path )
    if not m:
        raise ValueError( "{} needs to contain a run date of the format YYYY_MM_DD".format(path) )
    return m.group( 0 )

