import os
import os.path
import sys
from glob import glob
import shutil
import subprocess
import datetime
import logging
import fnmatch

from wrairlib.runfiletitanium import RunFile, RunFileSample
from wrairnaming import Formatter

from wrairlib.settings import config

def get_all_( datadir, fmatch ):
    '''
        Given a datadir of read files locate all of them
        using the fnmatch functions and return their abspath
    '''
    # Ensure path is abs
    datadir = os.path.abspath( datadir )
    if not is_valid_abs_path( datadir ):
        raise ValueError( "{} is not a valid dir path".format( datadir ) )

    logging.debug( "Getting all {} inside of {}".format(fmatch, datadir) )
    files = glob( os.path.join( datadir, fmatch ) )
    logging.debug( "Found files: %s" % files )
    return files

def get_sff_files( sffdir ):
    '''
        Given an directory path return all the sff files in that path as a dictionary keyed
        by the numerical value just preceeding the .sff in the name
        Typically these are 454 SFF files from signal processing and represent a region each
    '''
    # The list of sff files
    sff_files = {int(os.path.basename( sff )[-6:-4]):os.path.abspath( sff ) for sff in glob( sffdir + '/*.sff' )}
    return sff_files

def get_all_sff( outputdir ):
    '''
        Given an output directory from running demultiplex
        Get all the sff files from that directory
        split up into sub lists of regions
    '''
    sff_files = {}
    outputdir = os.path.abspath( outputdir )
    for rdir in os.listdir( outputdir ):
        if os.path.isdir( os.path.join( outputdir, rdir ) ):
            logging.debug( "Compiling Region %s SFF files list" % rdir )
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
    # Parse the runfile
    rf = RunFile( open( runfile ) )
    # Start the mapping with just the regions split out
    mapping = {region:{} for region in rf.regions}
    # Root key should be by region
    for sample in rf.samples:
        mapping[sample.region]["454Reads.%s.sff" % sample.midkeyname] = demultiplex_sample_name( sample, rf.platform )
    
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
		date=sample.runfile.date.strftime( '%Y_%m_%d' ),
		virus=sample.genotype,
        region=sample.region,
		extension='sff'
    )

def exec_recursive( path, func, *args, **kwargs ):
    '''
        Execute func recursively on every file and directory inside of path
    '''
    for root, dirs, files in os.walk( path ):
        [func( os.path.join( root, fd ), *args, **kwargs ) for fd in dirs]
        [func( os.path.join( root, fd ), *args, **kwargs ) for fd in files]

def set_config_perms( path ):
    '''
        Change perms to what settings are set to
    '''
    owner = int( config['DEFAULT']['Owner'] )
    group = int( config['DEFAULT']['Group'] )
    perms = int( config['DEFAULT']['Perms'], 8 )
    set_perms( path, perms, owner, group )

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

def set_perms( path, perms, uid=os.getuid(), gid=os.getgid(), recursive=False ):
    '''
        Sets permissions, uid, gid on a path
    '''
    if not os.path.isabs( path ):
        raise ValueError( "{} is not a valid abs path".format(path) )

    if not isinstance( uid, int ):
        uid = int( uid )
    if not isinstance( gid, int ):
        gid = int( uid )
    if not isinstance( perms, int ):
        perms = int( perms, 8 )
        
    logging.debug( "Changed permissions of %s to %s" % (path, perms) )
    logging.debug( "Changed user:gid of %s to %s:%s" % (path, uid, gid) )

    try:
        os.chmod( path, perms )
        os.chown( path, uid, gid )
    except OSError as e:
        logging.warning( str(e) )

    if recursive:
        exec_recursive( path, set_perms, perms, uid, gid )

def set_perms_recursive( path, perms, uid=os.getuid(), gid=os.getgid() ):
    make_readonly_recursive( path )

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
