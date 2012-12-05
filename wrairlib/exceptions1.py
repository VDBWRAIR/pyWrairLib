import os.path

class TooManyReferenceFilesException( Exception ):
    def __init__( self, reference, files_found ):
        self.reference = reference
        self.files_found = files_found
    def __str__( self ):
        return "More than one reference file found for %s. %s" % (self.reference, ",".join( self.files_found ))

class TooFewReferenceFilesException( Exception ):
    def __init__( self, reference, files_found ):
        self.reference = reference
        self.files_found = files_found
    def __str__( self ):
        return "No reference files found for %s." % (self.reference)

class NoReferenceFileException( Exception ):
    def __init__( self, reference, dir ):
        self.reference = reference
        self.dir = dir
    def __str__( self ):
        return "No reference file for %s could be found in %s" % (self.reference, self.dir)

class fffInvalidProject( Exception ):
    """ 454 Invalid Project """
    def __init__( self, path ):
        self.path = path

    def __str__( self ):
        parts = os.path.split( self.path )
        return "Missing %s in %s" % (parts[1], parts[0])

class UnknownFormatException( Exception ):
    """ Just a generic exception for stuff """
    def __init__( self, msg ):
        self.msg = msg

    def __str__( self ):
        return self.msg

class MissingPermissionsException( Exception ):
    """ Generic missing permission for path exception """
    def __init__( self, path ):
        self.path = path

    def __str__( self ):
        return "Required permissions for %s are missing" % self.path
