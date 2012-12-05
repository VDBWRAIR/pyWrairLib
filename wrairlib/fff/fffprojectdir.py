#!/usr/bin/env python2.4

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
from pyWrairLib.parser.exceptions import UnknownProjectDirectoryFormatException

def parse_dir_path( path ):
    """
        Arguments:
            path -- The directory path to parse as a string

        Return:
            Dictionary object keyed by the different parts of the path

        Tests:
        >>> valid_paths = ['Examples/05_11_2012_1_TI-MID51_PR_2305_pH1N1/', '05_11_2012_1_TI-MID10_PR_2357_AH3', '05_11_2012_1_TI-MID94_Mix_FPJ00258__1to1000_CFI1471_AH3_pH1N1', '05_11_2012_1_TI-MID95_Mix_FPJ00258_CFI1471_1to1000_AH3_pH1N1', '/home/EIDRUdata/Data_seq454/2012_05_11/05_11_2012_1_TI-MID10_PR_2357_AH3','03_09_2012_2_TI-MID10_FLU_BTB_SV1189_Q_pH1N1', '06_30_2010_2-RL1_2848T_SwH1N1', '06_30_2010_2_RL12_PR_1587_CP3_infB']
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
        >>> parse_dir_path( "invalid_path" )
        Traceback (most recent call last):
        ...
        UnknownProjectDirectoryFormatException: Unknown Project Directory format encountered: (invalid_path) Expected a Format like: (?P<date>\d+_\d+_\d+)_\d+[-_]*(T[iI][-_])*(?P<midkey>[a-zA-Z0-9]+)_(?P<sample>[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*)_(?P<extra>.*)
    """
    pattern = "(?P<date>\d+_\d+_\d+)_\d+[-_]*(T[iI][-_])*(?P<midkey>[a-zA-Z0-9]+)_(?P<sample>[a-zA-Z0-9]+(_[a-zA-Z0-9]+)*)_(?P<extra>.*)"
    cpattern = re.compile( pattern )
    spath = os.path.split( path.rstrip( '/' ) )[1]
    match = cpattern.match( spath )
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

if __name__ == "__main__":
    # Import the path just below the current script's path
    sys.path.append( '../' )
    _test()
