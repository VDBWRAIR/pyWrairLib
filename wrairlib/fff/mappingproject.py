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

    def get_primer_file( self ):
        """
            Extract and return all Primer files stored in
            VectorDatabase tag

            Tests:
                >>> a = MappingProject( 'examples/454MappingProject.xml' )
                >>> b = a.get_primer_file()
                >>> print b
                /some/project/dir/Primers/swH1N1_FDFusion_primer.fasta
        """
        files_pattern = "(?:<VectorDatabase/>)|(?:<VectorDatabase>(.*)</VectorDatabase>)"
        results = re.search( files_pattern, self.__file_contents, re.S )
        try:
            primerfile = results.groups()
            assert len( primerfile ) == 1
            return primerfile[0]
        except AttributeError as e:
            raise ValueError( '%s does not have a VectorDatabase entry' % self.__file_path )
        except AssertionError as e:
            raise ValueError( '%s has more than one VectorDatabase entry' % self.__file_path )

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
