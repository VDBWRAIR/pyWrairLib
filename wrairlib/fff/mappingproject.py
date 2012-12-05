###
## Parse 454MappingProject.xml
###

import re
import sys

class MappingProject:
    __file_path = None
    __file_contents = None
    def __init__( self, file_path ):
        self.__file_path = file_path
        self.__read()

    def __read( self ):
        fh = open( self.__file_path, 'r' )
        self.__file_contents = fh.read()
        fh.close()

    def get_reference_files( self ):
        """
            Extract and return all reference files

            Tests:
                >>> a = MappingProject( 'examples/454MappingProject.xml' )
                >>> b = a.get_reference_files()
                >>> type( b ) == list
                True
        """
        files_pattern = "<ReferenceFiles>.*</ReferenceFiles>"
        path_pattern = "<Path>(.*)</Path>"
        results = re.search( files_pattern, self.__file_contents, re.S )
        results = re.findall( path_pattern, results.group() )
        return results

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    if len( sys.argv ) == 2:
        if sys.argv[1] == "--test":
            _test()
