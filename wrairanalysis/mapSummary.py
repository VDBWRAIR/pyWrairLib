#!/usr/bin/env python

##############################################################################
##  Author: Tyghe Vallard
##  Date: 3/21/2013
##  Email: vallardt@gmail.com
##  Purpose:
##   Given a directory containing gsMapper projects, this script will find
##    all 454RefStatus.txt files and compiles a single Excel spreadsheet
##    from them for all references used across all projects.
##    You can also specify a reference file to 'target' so that only the
##    references inside that file will be listed in the output excel file.
##  Version:
##      1.0 -
##          Initial Script
##############################################################################

import os
import os.path
import sys
from argparse import ArgumentParser, FileType

from Bio import SeqIO

from wrairlib.fff.fffprojectdir import ProjectDirectory

from refstatusxls import *

def ref_idents( reffile ):
    return [seq.id for seq in SeqIO.parse( reffile, 'fasta' )]

def get_gsdirs( path ):
    ''' Return all gs dirs in a path '''
    dirs = [os.path.join( path, f ) for f in os.listdir( path ) if os.path.isdir( os.path.join( path, f ) )]
    pdirs = []
    for d in dirs:
        try:
            pdirs.append( ProjectDirectory( d ) )
        except ValueError as e:
            if 'not a valid Gs Project Directory' in str( e ):
                # Skip this directory
                continue
            else:
                # Umm?
                raise e
    return pdirs

def make_workbook( projdir, output, reference = None ):
    # The parent workbook
    wb = start_workbook()

    ws = wb.add_sheet( 'All454Status' )
    ws = RefStatusXLS( sheet = ws )

    for pd in get_gsdirs( projdir ):
        # Setup a new project in the worksheet
        ws.set_new_project( pd )
        # If reference was specified then make sheet with only that reference
        if reference:
            ws.make_sheet( ref_idents( reference ) )
        else:
            ws.make_sheet()

    # Write the sheet to output
    wb.save( output )


def main( args ):
    make_workbook( args.projdir, args.output, args.reference )

def get_args( ):
    parser = ArgumentParser()

    parser.add_argument( '-d', dest='projdir', required=True, help='A directory mapSamples.py was run in' )
    parser.add_argument( '-r', '--reference', dest='reference', help='Reference file to only include in output' )
    parser.add_argument( '-o', dest='output', default='AllRefStatus.xls', help='Output file name[Default: ./AllRefStatus.xls]' )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main( get_args() )
