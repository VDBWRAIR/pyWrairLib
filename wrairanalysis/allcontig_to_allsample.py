#!/usr/bin/env python

##############################################################################
##  Author: Tyghe Vallard
##  Date: 3/21/2013
##  Email: vallardt@gmail.com
##  Purpose:
##      Given a single gsMapper project directory, merges the 
##      454AllContigs.fna and 454AllContigs.qual files into a single
##      .fastq file
##      Output is by default sent to STDOUT(screen) but can be set to a file
##      by using the -o option
##  Version:
##      1.0 -
##          Initial Script
##############################################################################

import sys
import os
import os.path
from argparse import ArgumentParser,FileType
import re

from wrairlib.util import write_fastaqual_to_fastq
from wrairlib.fff.fffprojectdir import get_sample_from_dir_path


# The replacement pattern for the contig
# contig followed by any number of 0's followed by at least one 1-9 digit followd by any number of digits
contig_pattern = r'^contig0*([1-9][0-9]*)'
contig_compiled_match = re.compile( contig_pattern )
sample_pattern = '^(.*?.\d+)\s+(.*?,\s+\d+..\d+\s+length=\d+\s+numreads=\d+)'
sample_compiled_match = re.compile( sample_pattern )

# Global sample name
# Has to be global for rename_seqid to work
samplename = None

def fq_from_projdir( projdirpath ):
    '''
        Return tuple of fasta, qual filehandles for 454AllContigs.fna, 454AllContigs.qual inside a gsMapper project directory
    '''
    # Determine assembly or mapping
    am_dir = [os.path.join( projdirpath, d ) for d in os.listdir( projdirpath ) if d in ('mapping', 'assembly')]
    if len( am_dir ) != 1:
        raise ValueError( "Invalid gs project directory path given: %s" % projdirpath )

    path = am_dir[0]

    return open( os.path.join( path, '454AllContigs.fna' ) ), open( os.path.join( path, '454AllContigs.qual' ) )

def rename_seqid( seqtitle ):
    global contig_compiled_match
    
    # Perform the replacement
    replaced = contig_compiled_match.sub( r'%s.\1 ' % samplename, seqtitle )

    # It wasn't replaced correctly
    if replaced.startswith( 'contig' ):
        raise ValueError( "Sequence title [%s] is in an unkown format. Err 1" % seqtitle )

    # Now match the sample regex
    m = sample_compiled_match.search( replaced )
    if not m:
        raise ValueError( "Sequence title [%s] is in an unkown format. Err 2" % replaced )

    # Apparently only the id and description are
    # outputed on a write operation for Bio.SeqIO
    id, desc = m.groups()
    return id, ' ', desc
    
def to_allsample( gsprojdir, outputfile ):
    global samplename

    # Get filehandles for 454Allcontigs.* files
    fastah, qualh = fq_from_projdir( gsprojdir )

    # Set the global variable for samplename for title2id to work
    samplename = get_sample_from_dir_path( gsprojdir )

    # Write the records
    records = write_fastaqual_to_fastq( fastah, qualh, outputfile, title2ids=rename_seqid )

    # Return # records written
    return records

def main( args ):
    to_allsample( args.projdir, args.output )

def get_args( ):
    parser = ArgumentParser( )

    parser.add_argument( '-p', '--project-directory', dest='projdir', required=True, help='The project directory to gather 454AllContigs.* from' )
    parser.add_argument( '-o', '--output', dest='output', default=sys.stdout, type=FileType('w'), help='Where to output the results[Default: STDOUT]' )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main( get_args() )
