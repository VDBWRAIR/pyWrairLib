#!/usr/bin/env python

###############################################################################
##  Author: Tyghe Vallard
##  Date: 4/10/2013
##  Email: vallardt@gmail.com
##  Purpose:
##      This script is intended to handle renaming and formatting
##      reference sequences so they conform to the naming standards.
##
##      There are quite a few assumptions about the original reference file that
##      are being made for this version of the script.
##      First, is that all the necessary pieces of information are contained in
##      each of the identifiers. At a minimum there has to be
##          - Virus name
##          - Segment Abbreviation
##          - Segment Number
##          - Accession
##          - Location
##          - Isolate
##          - Year of collection
##     Obviously, not all viruses will contain all of this(i.e. Dengue...)
##      that will be revised in future versions.
##     It is quite handy that you can specify the -r option and then specify
##      as many reference files as you want using bash expansion
##      I.E *.fasta or *.fna ....
##  Version:
##      - 1.0
##          Initial Script
##          project.
##  TODO:
##   - Make it easier for viruses like Dengue to work
###############################################################################

import re
from argparse import ArgumentParser
import shutil
import logging
import os
import os.path


logging.basicConfig( level=logging.DEBUG )

def parse_identifier( identifier, pattern ):
    ''' Parse an identifier into the pieces inside of pattern '''
    # Ensure pattern is compiled
    if isinstance( pattern, str ):
        pattern = re.compile( pattern )

    m = pattern.search( identifier )
    # If the match worked
    if m:
        return m.groupdict()
    else:
        raise ValueError( "%s did not match %s" % (identifier, pattern.pattern) )

def read_ref( reffile ):
    ''' Return the entire file's contents '''
    contents = ''
    if isinstance( reffile, str ):
        with open( reffile ) as fh:
            contents = fh.read()
    elif hasattr( reffile, read ):
        contents = reffile.read()
    else:
        raise ValueError( "%s is not a valid file object or name of file" % reffile )

    return contents

def write_contents( contents, outputfile ):
    ''' Write the reference to the outputfile '''
    # If the contents are a list then join them
    if isinstance( contents, list ):
        joinstr = ""
        # Ensure that the lines are joined by a newline but
        # don't add an additional one
        if contents[0][-1] != '\n':
            joinstr = "\n"
        contents = joinstr.join( contents )

    # Write the contents of the file, truncating anything that was there before
    with open( outputfile, 'w' ) as fh:
        fh.write( contents )

def fix_identifier( identifier, pattern, correct_format ):
    ''' Return identifier replaced with correct identifier using pattern '''
    # Parse the identifier into a dictionary of information
    identinfo = parse_identifier( identifier, pattern )
    # Return the formatted correct identifier
    ident = correct_format.format( **identinfo )
    logging.debug( "%s --> %s" % (identifier, ident) )
    return ident

def fix_identifiers( reffile, pattern, correct_format ):
    ''' Replace all identifiers with correct names '''
    # Get contents as list
    lines = read_ref( reffile ).split( '\n' )
    for i in range( len( lines ) ):
        # Modify every line that starts with a > (identifier line)
        if lines[i].startswith( '>' ):
            lines[i] = fix_identifier( lines[i], pattern, correct_format )
    # Write the file back
    write_contents( lines, reffile )

def fix_filename( reffile, fileformat, pattern ):
    ''' Fix reference filename if needed '''
    filename = os.path.basename( reffile )
    basepath = os.path.dirname( reffile )
    # Parse first identifier to extract necessary pieces
    identinfo = {}
    # Read lines until identifier is encountered
    with open( reffile ) as fh:
        line = fh.readline().strip()
        # Just in case the first line is not an identifier
        # Read lines until one is found
        while not line.startswith( '>' ):
            line = fh.readline().strip()
        identinfo = parse_identifier( line, pattern )
    # Check filename
    # Rename if necessary
    logging.debug( "Identinfo to rename file: %s" % identinfo )
    logging.debug( "Filename format to fill: %s" % fileformat )
    correct_name = fileformat.format( **identinfo )
    if correct_name != filename:
        newpath = os.path.join( basepath, correct_name )
        logging.info( "Incorrect name for reference %s. Renaming to %s" % (reffile, newpath) )
        shutil.move( reffile, newpath )

def fix_file( reffile, identpattern, refidentformat, reffileformat, reffileformatpattern ):
    fix_identifiers( reffile, identpattern, refidentformat )
    fix_filename( reffile, reffileformat, reffileformatpattern )

def get_args( ):
    parser = ArgumentParser()

    parser.add_argument( '-r', '--reference', dest='reffile', nargs='+', required=True, help='Reference file to rename' )
    parser.add_argument( '-p', '--pattern', dest='pattern', default=REFERENCE_IDENTIFIER_PATTERN, help='Pattern to match each identifier[Default: %s]' % REFERENCE_IDENTIFIER_PATTERN )

    return parser.parse_args()
    
def main( args ):
    for rfile in args.reffile:
        fix_file( rfile, args.pattern, REFERENCE_IDENTIFIER_FORMAT, REFERENCE_FILE_FORMAT, REFERENCE_IDENTIFIER_FORMAT_PATTERN )

if __name__ == '__main__':
    args = get_args()
    main( args )
