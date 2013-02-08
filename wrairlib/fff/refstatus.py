###
## Parse 454RefStatus.txt
###

import re
import sys
from csv import DictReader

class RefStatus:
    def __init__( self, file_path ):
        self.__file_path = file_path
        self.__read()
        self.__parse()

    def __read( self ):
        fh = open( self.__file_path )
        self.__file_contents = fh.read()
        fh.close()

    def __parse( self ):
        lines = self.__file_contents.split( '\n' )[1:-1]
        self.ref_status = {}
        for line in lines:
            s = line.split( '\t' )
            self.ref_status[s[0]] = s[1:-1]

    def get_likely_reference( self ):
        """
            Returns the name of the most likely reference
            that was selected
            
            >>> rs = RefStatus( 'examples/gsMappingDir/mapping/454RefStatus.txt' )
            >>> rs.get_likely_reference()
            'CY074922_PB2_Managua09'
            >>> rs = RefStatus( 'examples/05_11_2012_1_TI-MID51_PR_2305_pH1N1/mapping/454RefStatus.txt' )
            >>> rs.get_likely_reference()
            'FJ969514_NS_California04'
            >>> rs = RefStatus( 'examples/05_11_2012_1_TI-MID10_PR_2357_AH3/mapping/454RefStatus.txt' )
            >>> rs.get_likely_reference()
            'CY074922_PB2_Managua09'
        """
        return self.__file_contents.split( '\n' )[2].split( '\t' )[0]

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    if len( sys.argv ) == 2:
        if sys.argv[1] == "--test":
            _test()
