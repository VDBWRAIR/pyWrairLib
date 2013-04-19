#!/usr/bin/env python

##########################################################################
##                       454projectdir
##	Author: Tyghe Vallard						                        
##	Date: 6/5/2012							                            
##	Version: 1.0							                            
##	Description:							                            
##      Defines how to parse a Project directory path into different parts
##      
#########################################################################

import sys
import re
import os
import os.path
import pprint

'''
if __name__ == "__main__":
    # Import the path just below the current script's path
    sys.path.insert( 0, os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) ) ) )
'''

from wrairlib.parser.exceptions import UnknownProjectDirectoryFormatException
from wrairlib.fff.fileparsers import refstatus, alignmentinfo, mappingproject, newblerprogress

from Bio import SeqIO

class MissingProjectFile(Exception):
    pass

class ProjectDirectory( object ):
    # Set static variables
    MAPPING = 'mapping'
    ASSEMBLY = 'assembly'
    UNKNOWN = 'unkown'

    def __init__( self, dirpath = os.getcwd() ):
        r'''
            # Just test to make sure nothing goes haywire when importing project
            >>> valid = [ "05_11_2012_1_TI-MID10_PR_2357_AH3", "05_11_2012_1_TI-MID51_PR_2305_pH1N1", "08_06_2012_1_Ti-MID30_D84_140_Dengue3", "08_31_2012_3_RL10_600Yu_10_VOID" ]
            >>> for pd in valid:
            ...   a = ProjectDirectory( os.path.join( 'examples', pd ) )
            >>> try:
            ...   ProjectDirectory( 'chicken' )
            ... except ValueError as e:
            ...   print "Caught"
            Caught
            >>> try:
            ...   ProjectDirectory( 'examples/InvalidDir1' )
            ... except ValueError as e:
            ...   print "Caught"
            Caught
            >>> try:
            ...   ProjectDirectory( 'examples/InvalidDir2' )
            ... except ValueError as e:
            ...   print "Caught"
            Caught
        '''
        # Set the base path to this project directory
        self.basepath = dirpath
        self._files = {}
        self._type = None
        if not self.isGsProjectDir( dirpath ):
            raise ValueError( "%s is not a valid Gs Project Directory" % dirpath )

    def get_file( self, name ):
        '''
            Retrieve a file path in the project by just it's name(with or without extension
            #>>> valid = [ "05_11_2012_1_TI-MID10_PR_2357_AH3", "05_11_2012_1_TI-MID51_PR_2305_pH1N1", "08_06_2012_1_Ti-MID30_D84_140_Dengue3", "08_31_2012_3_RL10_600Yu_10_VOID" ]
        '''
        # If it has period try splitting it and searching on that name
        if '.' in name:
            try:
                return self.files[os.path.splitext( os.path.basename( name ) )[0]]
            except KeyError as e:
                pass
        # Fall back on the entire name
        try:
            return self.files[name]
        except KeyError as e:
            pass
        # Try chopping of 454
        try:
            n = name.replace( '454', '' )
            return self.files[n]
        except KeyError as e:
            pass
        try:
            n = '454' + name
            return self.files[n]
        except KeyError as e:
            raise MissingProjectFile( "Project %s does not contain the file %s" % (self.basepath, name) )

    @property
    def files( self ):
        '''
            Return all the filenames under the mapping/assembly directory

            >>> valid = [ "05_11_2012_1_TI-MID10_PR_2357_AH3", "05_11_2012_1_TI-MID51_PR_2305_pH1N1", "08_06_2012_1_Ti-MID30_D84_140_Dengue3", "08_31_2012_3_RL10_600Yu_10_VOID" ]
            >>> for d in valid:
            ...   len( ProjectDirectory( 'examples/' + d ).files )
            19
            6
            32
            22
        '''
        # Only retreive file list once
        if not self._files:
            # Setup the files dictionary keyed by just filename without extension
            for pfile in os.listdir( self.path ):
                filename, fileext = os.path.splitext( os.path.basename( pfile ) )
                # Index full path by just the filename without extension
                self._files[filename] = os.path.join( self.path, pfile )
        return self._files

    def __getattr__( self, name ):
        '''
            Allows us to dynamically retrieve objects for files within the project

            >>> valid = [ "05_11_2012_1_TI-MID10_PR_2357_AH3", "05_11_2012_1_TI-MID51_PR_2305_pH1N1", "08_06_2012_1_Ti-MID30_D84_140_Dengue3", "08_31_2012_3_RL10_600Yu_10_VOID" ]
            >>> pd = ProjectDirectory( 'examples/' + valid[0] )
            >>> rf = pd.RefStatus
            >>> rf = pd.AlignmentInfo
            >>> rf = pd.MappingProject
            >>> rf = pd.NewblerProgress
            >>> try:
            ...   pd.Nope
            ... except AttributeError as e:
            ...   print "Caught"
            Caught
        '''
        # Fetch the filepath using the attribute name that was attempted
        try:
            filepath = self.get_file( name )
            # This is scary as I'm not entirely sure how it works
            module = globals()[name.lower()]
            # Once the module is grabbed then return the instance
            return getattr( module, name )( filepath )
        except (ValueError,KeyError) as e:
            raise AttributeError( "No fileparser for %s(%s)" % (name,str(e)) )

    @property
    def path( self ):
        ''' The path to the actual mapping/assembly information '''
        return os.path.join( self.basepath, self.project_type )

    @property
    def project_type( self ):
        ''' Mapping or Assembly Project '''
        if self._type is not None:
            return self._type
        if os.path.isdir( os.path.join( self.basepath, self.MAPPING ) ):
            return self.MAPPING
        elif os.path.isdir( os.path.join( self.basepath, self.ASSEMBLY ) ):
            return self.ASSEMBLY
        else:
            return self.UNKNOWN

    def isGsProjectDir( self, path ):
        '''
            Is the path given a gsMapper or gsAssembly directory
            Aka, does it contain a 454Project.xml file and has either mapping or assembly dir
        '''
        test1 = os.path.isdir( path ) and os.path.exists( os.path.join( path, '454Project.xml' ) )
        return test1 and self.project_type != self.UNKNOWN

def reference_file_for_identifier( identifier, projdir ):
    """
        Arguments:
            identifier -- An identifier from 454RefStatus.txt to obtain the reference file for
    
        Return:
            reference file path or None if not found

        Tests:
            >>> reference_file_for_identifier( 'california', 'examples/05_11_2012_1_TI-MID10_PR_2357_AH3' )
            '/home/EIDRUdata/Tyghe/Dev/pyWrairLib/wrairlib/fff/examples/Ref/pdmH1N1_California.fasta'
            >>> reference_file_for_identifier( 'FJ969514_NS_California04', 'examples/05_11_2012_1_TI-MID51_PR_2305_pH1N1' )
            '/home/EIDRUdata/Tyghe/Dev/pyWrairLib/wrairlib/fff/examples/Ref/pdmH1N1_California.fasta'
            >>> reference_file_for_identifier( 'yankydoodle', 'examples/05_11_2012_1_TI-MID51_PR_2305_pH1N1' ) is None
            True
    """
    pd = ProjectDirectory( projdir )
    mp = pd.MappingProject
    refs = mp.get_reference_files()

    useref=None
    for ref in refs:
        refpath = ref
        try:
            for seq in SeqIO.parse( refpath, 'fasta' ):
                if identifier.lower() in seq.id.lower():
                    return refpath
        except IOError as e:
            sys.stderr.write( "Cannot read %s" % refpath )
            raise e

def parse_dir_path( path ):
    """
        Arguments:
            path -- The directory path to parse as a string

        Return:
            Dictionary object keyed by the different parts of the path

        Tests:
        >>> valid_paths = ['Examples/05_11_2012_1_TI-MID51_PR_2305_pH1N1/', '05_11_2012_1_TI-MID10_PR_2357_AH3', '05_11_2012_1_TI-MID94_Mix_FPJ00258__1to1000_CFI1471_AH3_pH1N1', '05_11_2012_1_TI-MID95_Mix_FPJ00258_CFI1471_1to1000_AH3_pH1N1', '/home/EIDRUdata/Data_seq454/2012_05_11/05_11_2012_1_TI-MID10_PR_2357_AH3','03_09_2012_2_TI-MID10_FLU_BTB_SV1189_Q_pH1N1', '06_30_2010_2-RL1_2848T_SwH1N1', '06_30_2010_2_RL12_PR_1587_CP3_infB','SAMPLE1__RL23__H3N2']
        >>> for p in valid_paths:
        ...   parse_dir_path( p )
        {'date': '05_11_2012', 'sample': 'PR_2305', 'midkey': 'MID51', 'extra': 'pH1N1'}
        {'date': '05_11_2012', 'sample': 'PR_2357', 'midkey': 'MID10', 'extra': 'AH3'}
        {'date': '05_11_2012', 'sample': 'Mix_FPJ00258', 'midkey': 'MID94', 'extra': '_1to1000_CFI1471_AH3_pH1N1'}
        {'date': '05_11_2012', 'sample': 'Mix_FPJ00258_CFI1471_1to1000_AH3', 'midkey': 'MID95', 'extra': 'pH1N1'}
        {'date': '05_11_2012', 'sample': 'PR_2357', 'midkey': 'MID10', 'extra': 'AH3'}
        {'date': '03_09_2012', 'sample': 'FLU_BTB_SV1189_Q', 'midkey': 'MID10', 'extra': 'pH1N1'}
        {'date': '06_30_2010', 'sample': '2848T', 'midkey': 'RL1', 'extra': 'SwH1N1'}
        {'date': '06_30_2010', 'sample': 'PR_1587_CP3', 'midkey': 'RL12', 'extra': 'infB'}
        {'sample': 'SAMPLE1', 'virus': 'H3N2', 'midkey': 'RL23'}
        >>> try:
        ...   parse_dir_path( "invalid_path" )
        ... except UnknownProjectDirectoryFormatException as e:
        ...   print "Caught"
        Caught
    """
    pattern = "(?P<date>\d+_\d+_\d+)_\d+[-_]*(T[iI][-_])*(?P<midkey>[a-zA-Z0-9]+)_(?P<sample>[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*)_(?P<extra>.*)"
    cpattern = re.compile( pattern )
    spath = os.path.split( path.rstrip( '/' ) )[1]
    match = cpattern.match( spath )
    if not match:
        # Try the newstyle directory names too
        pattern = "(?P<sample>.*?)__(?P<midkey>.*?)__(?P<virus>.*?)$"
        match = re.match( pattern, spath )
        if not match:
            raise UnknownProjectDirectoryFormatException( path, pattern )
    matchdict = match.groupdict()
    return matchdict

def get_midkey_from_dir_path( path ):
    """
        Arguments:
            path -- The directory path to get the midkey from
        Return:
            String containing the midkey

        Tests:
        >>> valid_paths = ['05_11_2012_1_TI-MID10_PR_2357_AH3', '05_11_2012_1_TI-MID94_Mix_FPJ00258__1to1000_CFI1471_AH3_pH1N1', '05_11_2012_1_TI-MID95_Mix_FPJ00258_CFI1471_1to1000_AH3_pH1N1']
        >>> for d in valid_paths:
        ...  get_midkey_from_dir_path( d )
        'MID10'
        'MID94'
        'MID95'
    """
    return parse_dir_path( path )['midkey']

def get_sample_from_dir_path( path ):
    """
        Arguments:
            path -- The directory path to get the sample name from
        Return:
            String containing the sample name

        Tests:
        >>> valid_paths = ['05_11_2012_1_TI-MID10_PR_2357_AH3', '05_11_2012_1_TI-MID94_Mix_FPJ00258__1to1000_CFI1471_AH3_pH1N1', '05_11_2012_1_TI-MID95_Mix_FPJ00258_CFI1471_1to1000_AH3_pH1N1']
        >>> for d in valid_paths:
        ...  get_sample_from_dir_path( d )
        'PR_2357'
        'Mix_FPJ00258'
        'Mix_FPJ00258_CFI1471_1to1000_AH3'
    """
    return parse_dir_path( path )['sample']

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
