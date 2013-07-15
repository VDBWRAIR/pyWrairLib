#!/usr/bin/env python

import sys
from argparse import ArgumentParser
from Bio import SeqIO

def main( ):
    args = parse_args()

    print_csv( parse_file( args.inputfile ) )

def print_csv( stats ):
    '''
        Prints the stats in a csv format to STDOUT for easy graphing

        @param stats - Output from parse_file
    '''
    # Print stat headers
    stat_headers = ['Pos','Min','Sum','Avg','Max','Depth']
    print ",".join( stat_headers )

    # Loop through stats
    for pos, stat in enumerate( stats, start=1 ):
        print "{},{}".format( pos, ','.join( [str(x) for x in stat] ) )

def parse_file( filename ):
    '''
        Parses the file into statistics about each base seen

        @param filename - File path to parse(.qual file)
        @return List of [(min, sum, avg, max, depth),...] for each base position.
    '''
    stats = []
    records_read = 0
    for record in SeqIO.parse( filename, 'qual' ):
        parse_read( record, stats )
        records_read += 1
        if records_read % 1000 == 0:
            sys.stderr.write( "{} records parsed\n".format( records_read ) )

    return stats

def parse_read( seq_record, running_stats ):
    '''
        Updates stats list with seq_records's information

        @param seq_record - Bio.seq record which should be a 454 qual record
        @param running_stats - List of [(min, sum, avg, max, depth),...] stats where each 
            index relates to a base position

        >>> from Bio.SeqRecord import SeqRecord
        >>> from Bio.Seq import UnknownSeq
        >>> sr = SeqRecord( UnknownSeq( 3 ) )
        >>> sr.letter_annotations = {'phred_quality': [35, 40, 1]}
        >>> rs = []
        >>> parse_read( sr, rs )
        >>> assert rs == [(35,35,35.0,35,1),(40,40,40.0,40,1),(1,1,1.0,1,1)], rs
        >>> sr2 = SeqRecord( UnknownSeq( 4 ) )
        >>> sr2.letter_annotations = {'phred_quality': [35, 40, 2, 2]}
        >>> parse_read( sr2, rs )
        >>> assert rs == [(35,70,35.0,35,2),(40,80,40.0,40,2),(1,3,1.5,2,2),(2,2,2.0,2,1)], rs
    '''
    # Quality scores as a list
    quals = seq_record.letter_annotations['phred_quality']
    for i in range( len( quals ) ):
        # Check to see if we have seen this position yet
        if not len( running_stats ) > i or not isinstance( running_stats[i], tuple ):
            running_stats.append( (100,0,0,0,0) )
        minq, sumq, avgq, maxq, depth = running_stats[i]
        minq = min( quals[i], minq )
        sumq += quals[i]
        maxq = max( quals[i], maxq )
        depth = depth + 1
        avgq = sumq * 1.0 / depth
        running_stats[i] = (minq, sumq, avgq, maxq, depth)

def parse_args( ):
    parser = ArgumentParser( description='Parse a .qual file into statistics about'\
        'each base' )

    parser.add_argument( dest='inputfile', help='The qual file to parse' )

    return parser.parse_args()

if __name__ == '__main__':
    main()
