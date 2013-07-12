#!/usr/bin/env python

import os
import os.path
import sys
from argparse import ArgumentParser
from Bio import SeqIO
from glob import glob

def main( ):
    args = parse_args()

    if os.path.isdir( args.input ):
        sffs = glob.glob( args.input + '/*.sff' )
    elif os.path.exists( args.input ):
        sffs = [args.input]
    else:
        raise ValueError( "{} is not a valid directory or sff file".format(args.input) )

    # Convert all input sff to fastq
    for sff in sffs:
        bn, ext = os.path.splitext( sff )
        outname = bn + '.fastq'
        SeqIO.write( SeqIO.parse( sff, 'sff' ), outname, 'fastq' )

def parse_args( ):
    parser = ArgumentParser( description='Convert sff file to fastq' )

    parser.add_argument( dest='input', help='Directory or sff file to convert' )

    return parser.parse_args()

if __name__ == '__main__':
    main()
