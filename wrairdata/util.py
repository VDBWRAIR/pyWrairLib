import os
import os.path
import sys
from glob import glob
import shutil
import subprocess
import datetime
import logging
import fnmatch

from wrairlib.fff.runfiletitanium import RunFile, RunFileSample
from wrairlib.util import get_all_

try:
    from wrairdata import settings
except ImportError as e:
    sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) )
    from wrairdata import settings

def get_sff_files( sffdir ):
    '''
        Given an directory path return all the sff files in that path as a dictionary keyed
        by the numerical value just preceeding the .sff in the name

        >>> fp = '../../ReadData/Roche454/D_2013_03_13_13_56_26_vnode_signalProcessing/'
        >>> s = get_sff_files( fp + 'sff' )
        >>> assert {1: '/home/EIDRUdata/NGSData/ReadData/Roche454/D_2013_03_13_13_56_26_vnode_signalProcessing/sff/H52E4QC01.sff', 2: '/home/EIDRUdata/NGSData/ReadData/Roche454/D_2013_03_13_13_56_26_vnode_signalProcessing/sff/H52E4QC02.sff'} == s
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
        mapping[sample.region]["454Reads.%s.sff" % sample.midkeyname] = demultiplex_sample_name( sample )
    
    return mapping

def demultiplex_sample_name( sample ):
    r'''
        Return a demultiplexed sff file name from a given RunFileSample instance
    '''
    return settings.READ_FILENAME_PATTERN % (sample.name, sample.midkeyname, 
            sample.runfile.date.strftime( "%Y_%m_%d" ), sample.genotype, 'sff')

def exec_recursive( path, func, *args, **kwargs ):
    '''
        Execute func recursively on every file and directory inside of path

        >>> import tempfile
        >>> d = tempfile.mkdtemp()
        >>> f = [open( os.path.join( d, str(f) ), 'w' ) for f in range( 3 )]
        >>> os.mkdir( os.path.join( d, 'tmp1' ) )
        >>> df = [open( os.path.join( d, 'tmp1', str(f) ), 'w' ) for f in range( 3 )]

        #>>> exec_recursive( d, unlink )
    '''
    for root, dirs, files in os.walk( path ):
        [func( os.path.join( root, fd ), *args, **kwargs ) for fd in dirs]
        [func( os.path.join( root, fd ), *args, **kwargs ) for fd in files]

def make_readonly( path ):
    owner = settings.OWNER
    group = settings.GROUP
    perms = settings.PERMS
    os.chmod( path, perms )
    os.chown( path, owner, group )
    logging.debug( "Changed permissions of %s to %s" % (path, perms) )
    logging.debug( "Changed user:group of %s to %s:%s" % (path, owner, group) )

def make_readonly_recursive( rootpath ):
    make_readonly( rootpath )
    exec_recursive( rootpath, make_readonly )
    exec_recursive( rootpath, make_readonly )

if __name__ == '__main__':
    import doctest
    doctest.testmod()
