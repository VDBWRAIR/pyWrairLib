class UnknownIdentifierLineException( Exception ):
    def __init__(self, line):
        self.line = line
    def __str__( self ):
        return "Unknown Identifier Line: %s" % self.line

class UnknownProjectDirectoryFormatException( Exception ):
    def __init__(self, path, expected):
        self.path = path
        self.expected = expected
    def __str__( self ):
        return "Unknown Project Directory format encountered: (%s) Expected a Format like: %s" % (self.path,self.expected)
