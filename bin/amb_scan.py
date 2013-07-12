#!/usr/bin/env python

import pysam

from argparse import ArgumentParser
import os
import os.path
import sys
import pprint

# Any bases found not in this string will be counted as ambiguous
DNABASES = 'ATGC'

def main():
    args = parse_args()

    if not os.path.exists( args.bam ):
        print "{} does not exist".format( args.bam )
        sys.exit( -1 )

    start = int( args.rstart )
    end = int( args.rend )
    if start >= end:
        print "{} is not larger than {}".format( end, start )
        sys.exit( -1 )

    # Open the sam
    bam = pysam.Samfile( args.bam )
    # Get the reference
    ref = bam.references[0]
    # This will hold each read's statistics
    # 'read': {'ambiguities': 0}
    reads = {}
    # Iterate over every read in the alignment(Iterate down)
    for read in bam.fetch( ):
        # Iterate over all of the bases(Iterate right)
        # Enumerate so each base is indexed(Zero indexed, be warned)
        # read.pos is the position of first base in alignment(aka read.seq[1] is actually pos read.pos in the alignment)
        for i, base in enumerate( read.seq, read.pos ):
            # Only interested in the bases between start and end(Don't forget these are 0 indexed)
            if i in range( start+1, end ):
                if base.lower() not in DNABASES.lower():
                    # Make sure the read name is in stats dictionary
                    if read.qname not in reads:
                        # Initialize stats for this read
                        reads[read.qname] = {'ambiguities': 1}
                    else:
                        reads[read.qname]['ambiguities'] += 1

    print_csv( reads )

def print_csv( read_stats ):
    for read_name, stats in sorted( read_stats.items() ):
        print "{},{}".format(read_name,stats['ambiguities'])
        
def parse_args():
    parser = ArgumentParser()

    parser.add_argument( dest='bam', help='Bamfile path' )
    parser.add_argument( dest='rstart', help='Region start' )
    parser.add_argument( dest='rend', help='Region end' )

    return parser.parse_args()

if __name__ == '__main__':
    main()
