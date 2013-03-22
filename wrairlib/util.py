#!/usr/bin/env python

##########################################################################
##                       util.py
##	Author: Tyghe Vallard						                        
##	Date: 6/12/2012							                            
##	Version: 1.0							                            
##	Description:							                            
##      Provides utility functions for various tasks
##########################################################################

import os
import re
import sys

from exceptions1 import *

try:
    from Bio import SeqIO
    from Bio.SeqIO.QualityIO import PairedFastaQualIterator

except ImportError:
    print "Please make sure BioPython is installed. You can try pip install biopython on the command line"
    sys.exit( 1 )

# WRAIR common fasta extensions
FASTA_EXTENSIONS = ['fasta','fna','fas']

def search_refs( refs, search_term, ext_only = None ):
    """
        Provides similar functionality as grep "<search_term>" <dir_path>/*
        
        Arguments:
            refs -- List of reference files to search through
            search_term -- The term to search for
            ext_only -- See list_dir for description of this argument as it is simply passed straight through to that function

        Return:
            List of tuples of files that contain the search term and the line in that file that it was found

        Tests:
        >>> files = ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta']
        >>> print search_refs( files, '>GQ377049_PB1_California04', FASTA_EXTENSIONS )
        [('Examples/Ref/pdmH1N1_California.fasta', 35)]
        >>> print search_refs( files, 'CANTFINDME&@^&', FASTA_EXTENSIONS )
        []
        >>> print search_refs( files, 'CANTFINDME&@^&', FASTA_EXTENSIONS )
        []
    """
    found = []
    for f in refs:
        line_count = 1
        # Loop through the 
        for line in open( f ):
            # Search for term in the current line
            if search_term in line:
                found.append( (f, line_count) )
            line_count += 1
    return found

def list_dir( dir_path, ext_only = None ):
    """
        Lists contens of a directory
        
        Arguments:
            dir_path -- Path to directory to be searched in(non recursively)
            ext_only -- Either list or string of file extensions that are valid and will be searched
                        Extensions can contain the period or they can be without
                        If None is supplied then all files and directories are listed
    
        Return:
            List of files & directories in the dir_path
            Empty list if invalid path is given
        
        Tests:
        >>> print list_dir( 'Examples/Ref' )
        ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta', 'Examples/Ref/other_file.c']
        >>> print list_dir( 'Examples/Ref/', )
        ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta', 'Examples/Ref/other_file.c']
        >>> print list_dir( './Examples/Ref/' )
        ['./Examples/Ref/infB_Victoria.fasta', './Examples/Ref/pdmH1N1_California.fasta', './Examples/Ref/H3N2_Managua.fasta', './Examples/Ref/H5N1_Thailand.fasta', './Examples/Ref/H1N1_boston.fasta', './Examples/Ref/pdmH1N1_California2.fasta', './Examples/Ref/other_file.c']
        >>> print list_dir( 'Examples/Ref', 'fasta' )
        ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta']
        >>> print list_dir( 'Examples/Ref', '.fasta' )
        ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta']
        >>> print list_dir( 'Examples/Ref/', ['.fasta', '.fna'] )
        ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta']
        >>> print list_dir( 'Examples/Ref/', ['fasta'] )
        ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta']
    """
    # If a path that does not exist is given then return empty list
    if not os.path.exists( dir_path ):
        return []
    files = os.listdir( dir_path )
    # If ext_only is a string then compare only that string with the extension
    if type( ext_only ) == str:
        # Strip off the leading '.'
        ext_only = ext_only.lstrip( '\.' )
        files = [os.path.join( dir_path, f ) for f in files if os.path.splitext( f )[1].lstrip( '\.' ) == ext_only ]
    # If ext_only is a list then check each item in the list to see if it has a valid extension
    elif type( ext_only ) == list:
        # Strip off the leading '.'
        ext_only = [f.lstrip( '\.' ) for f in ext_only]
        files = [os.path.join( dir_path, f ) for f in files if os.path.splitext( f )[1].lstrip( '\.' ) in ext_only]
    else:
        files = [os.path.join( dir_path, f ) for f in files]
    return files

def find_reference_file_for( reference, refs, ext = FASTA_EXTENSIONS ):
    """
        Locates the reference file for a given reference inside a directory
            of fasta files or a list of reference files
        
        Arguments:
            reference -- String representing the reference to search for
            refs -- Reference directory or list of references to search in
            ext -- see list_dir for more info on this parameter

        Return:
            Returns the a tuple of the file with the reference and what line it is on
                If more than 1 file is found then an TooManyReferenceFilesException is thrown

        Tests:
        >>> find_reference_file_for( '>GQ377049_PB1_California04', 'Examples/Ref' )
        Traceback (most recent call last):
        ...
        TooManyReferenceFilesException: More than one reference file found for >GQ377049_PB1_California04. Examples/Ref/pdmH1N1_California.fasta,Examples/Ref/pdmH1N1_California2.fasta
        >>> print find_reference_file_for( '>CY081008_PB2_Boston09', 'Examples/Ref' )
        ('Examples/Ref/H1N1_boston.fasta', 1)
        >>> find_reference_file_for( 'NOPECANTfindME', 'Examples/Ref' )
        Traceback (most recent call last):
        ...
        NoReferenceFileException: No reference file for NOPECANTfindME could be found in Examples/Ref
        >>> refs = ['Examples/Ref/infB_Victoria.fasta', 'Examples/Ref/pdmH1N1_California.fasta', 'Examples/Ref/H3N2_Managua.fasta', 'Examples/Ref/H5N1_Thailand.fasta', 'Examples/Ref/H1N1_boston.fasta', 'Examples/Ref/pdmH1N1_California2.fasta']
        >>> find_reference_file_for( '>CY081003_NA_Boston09', refs )
        ('Examples/Ref/H1N1_boston.fasta', 153)
    """
    file_list = refs
    if type( refs ) != list:
        file_list = list_dir( refs, ext )
    files = search_refs( file_list, reference, ext )
    if len( files ) > 1:
        raise TooManyReferenceFilesException( reference, [f[0] for f in files] )
    elif len( files ) == 0:
        raise NoReferenceFileException( reference, refs )
    return files[0]

def get_gap_sequence_length( reference, ref_path, ext = FASTA_EXTENSIONS ):
    """
        Fetches the total sequence length of a reference sequence

        Arguments:
            reference -- String representing the reference to find
            ref_path -- Directory to search for the reference in

        Return:
            integer representing the reference sequence length

        Tests:
        >>> get_gap_sequence_length( '>GQ377049_PB1_California04', 'Examples/Ref' )
        Traceback (most recent call last):
        ...
        TooManyReferenceFilesException: More than one reference file found for >GQ377049_PB1_California04. Examples/Ref/pdmH1N1_California.fasta,Examples/Ref/pdmH1N1_California2.fasta
        >>> get_gap_sequence_length( '>CY081008_PB2_Boston09', 'Examples/Ref' )
        2314
    """
    length = 0
    # Get the file and position of reference
    file = find_reference_file_for( reference, ref_path, ext )

    # Get an index'd record of the file
    records = SeqIO.index( file[0], 'fasta' )
    
    # Gather the length of that record
    ref = reference
    if reference[0] == '>':
        ref = reference[1:]
    length = len( records[ref] )
    
    return length

def get_idents_from_reference( ref_path ):
    """
        Returns all of the genes found in the identifier lines in a given reference file path

        Arguments:
            ref_path -- Full path to a reference file to read and get the genes from 

        Return:
            list containing all of the gene names

        Tests:
        >>> refs = ["H1N1_boston.fasta", "H3N2_Managua.fasta", "H5N1_Thailand.fasta", "infB_Victoria.fasta", "pdmH1N1_California2.fasta", "pdmH1N1_California.fasta"]
        >>> for r in refs:
        ...   get_idents_from_reference( os.path.join( "Examples", "Ref", r ) )
        ['CY081008_PB2_Boston09', 'CY081007_PB1_Boston09', 'CY081006_PA_Boston09', 'CY081001_HA_Boston09', 'CY081004_NP_Boston09', 'CY081003_NA_Boston09', 'CY081002_MP_Boston09', 'CY081005_NS_Boston09']
        ['CY074922_PB2_Managua09', 'CY074921_PB1_Managua09', 'CY074920_PA_Managua09', 'CY074915_HA_Managua09', 'CY074918_NP_Managua09', 'CY074917_NA_Managua09', 'CY074916_MP_Managua09', 'CY074919_NS_Managua09']
        ['Human/1_(PB2)/H5N1/1/Thailand/2004', 'Human/2_(PB1)/H5N1/2/Thailand/2004', 'Human/3_(PA)/H5N1/3/Thailand/2004', 'Human/4_(HA)/H5N1/4/Thailand/2004', 'Human/5_(NP)/H5N1/5/Thailand/2004', 'Human/6_(NA)/H5N1/6/Thailand/2004', 'Human/7_(MP)/H5N1/7/Thailand/2004', 'Human/8_(NS)/H5N1/8/Thailand/2004']
        ['CY040449_B/Malaysia/2506/2004/4(HA)', 'CY040450_B/Malaysia/2506/2004/7(MP)', 'CY040451_B/Malaysia/2506/2004/6(NA)', 'CY040452_B/Malaysia/2506/2004/5(NP)', 'CY040453_B/Malaysia/2506/2004/8(NS)', 'CY040454_B/Malaysia/2506/2004/3(PA)', 'CY040455_B/Malaysia/2506/2004/1(PB1)', 'CY040456_B/Malaysia/2506/2004/2(PB2)']
        ['FJ969516_PB2_California04', 'GQ377049_PB1_California04', 'FJ969515_PA_California04', 'GQ117044_HA_California04', 'FJ969512_NP_California04', 'FJ969517_NA_California04', 'FJ969513_MP_California04', 'FJ969514_NS_California04']
        ['FJ969516_PB2_California04', 'GQ377049_PB1_California04', 'FJ969515_PA_California04', 'GQ117044_HA_California04', 'FJ969512_NP_California04', 'FJ969517_NA_California04', 'FJ969513_MP_California04', 'FJ969514_NS_California04']
    """
    # Pattern to match genes
    cp = '>(\S+)'

    # Open the file and find all matches from the pattern
    fh = open( ref_path )
    genes = re.findall( cp, fh.read() )
    fh.close()

    # Return the finds
    return genes

def pretty_print( d, indent = 0 ):
    for key, value in d.iteritems():
        print '\t' * indent + str( key )
        if isinstance( value, dict ):
            pretty_print( value, indent +1 )
        else:
            print '\t' * (indent+1) + str( value )

def write_fastaqual_to_fastq( fastafile, qualfile, outputfile, title2ids=None ):
    records = fastaqual_to_fastq( fastafile, qualfile, title2ids=title2ids )
    count = SeqIO.write( records, outputfile, "fastq" )
    return count

def fastaqual_to_fastq( fastafile, qualfile, title2ids=None ):
    records = PairedFastaQualIterator( fastafile, qualfile, title2ids=title2ids )
    return records

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    # Import the path just below the current script's path
    _test()
