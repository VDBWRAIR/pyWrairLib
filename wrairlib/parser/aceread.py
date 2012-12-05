#!/usr/bin/env python

# Biopython Imports
from Bio.Sequencing import Ace as ace

# Python Imports
import sys

class Ace:
    def __init__( self, acefile ):
        self.ace_filename = acefile

    def _get_gen( self ):
        return ace.parse( open( self.ace_filename ) )

    def has_contig( self, contigname ):
        for contig in self._get_gen():
            if contig.name == contigname:
                return True
        return False

    def reads_for_contig( self, contigname ):
        reads = []
        for contig in self._get_gen():
            if contig.name == contigname:
                for read in contig.reads:
                    reads.append( read.rd.name )

        return reads
