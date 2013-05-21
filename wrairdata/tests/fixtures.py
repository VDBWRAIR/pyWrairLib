import os
import os.path
import glob
import re

FIXTURE_PATH = os.path.join( os.path.dirname( __file__ ), 'fixtures' )
MIDPARSE = os.path.join( FIXTURE_PATH, 'MidParse.conf' )
DEMULTIPLEX_BY_REGION_PATH = os.path.join( FIXTURE_PATH, 'demultiplex_by_region' )
RUNFILE_PATH = os.path.join( FIXTURE_PATH, 'RunfileFlxPlus_2013_05_01.txt' )

with open( MIDPARSE ) as fh:
    MIDPREFIX = fh.readlines()[0].strip()

def demultiplex_reads_lst( ):
    '''
        Just return the .lst fixtures name.lst:{barcode:numreads} 
        from the output of sfffile -s
    '''
    lsts = glob.glob( os.path.join( FIXTURE_PATH, '*.lst' ) )
    readlists = {}
    return {os.path.basename(lst):lst for lst in lsts}

def mock_demultiplex_directory( demultiplex_dir = DEMULTIPLEX_BY_REGION_PATH ):
    '''
        Return dictionary keyed by regions inside of mock demultiplexed directory
        Each region contains just the filenames contained within it
    '''
    retd = {}
    for d in os.listdir( demultiplex_dir ):
        retd[int(d)] = os.listdir( os.path.join( demultiplex_dir, d ) )
    return retd

def multiplex_sffs():
    ''' multiplex sff dict name:path '''
    return {os.path.basename(path):path for path in glob.glob( os.path.join( FIXTURE_PATH, '*.sff' ) )}
