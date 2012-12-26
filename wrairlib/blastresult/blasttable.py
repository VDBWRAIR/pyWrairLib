import re
from wrairlib.exceptions1 import *

class BlastResult:
    def __init__( self, blastfilepath ):
        self.blast_filepath = blastfilepath

    def topResults( self ):
        """
            Return top results for each unique identifier
            Identifier is the furthest left column(ASSUMPTION!!!)
        """
        for ident in self.getUniqueIdentifiers():
            tr = self.topResult( ident )
            if not tr:
                raise ValueError( "%s has no top result" % ident )
            yield tr

    def getUniqueIdentifiers( self ):
        """
            Return a list of all the unique identifiers
        """
        # Set returns only the unique set from a given list
        return set( [row.ident for row in self._parse()] )

    def topResult( self, identifier ):
        """
            Return the top result for a given identifer
            Identifier is the furthest left column(ASSUMPTION!!!)
        """
        # Hold the very top in case nothing is found we can return it instead
        verytop = None
        # Loop through each row in the table
        for row in self._parse():
            # If the identifier matches the one we are looking for
            if row.ident == identifier:
                # If verytop is not set set it
                if not verytop:
                    verytop = row
                # If the tax id is not -1
                if row.genusid != -1:
                    # Return this row(It will be the top result)
                    return row
        return verytop

    def _parse( self ):
        """
            Generator yielding a BlastResultRow for each line in the table
        """
        fh = open( self.blast_filepath )
        # Finished flag in case summary info is found
        finished = False
        # Seen header line?
        seenheaderline = False
        for l in fh:
            line = l.strip()

            # Only do this for the first line
            if not seenheaderline:
                seenheaderline = True
                # If no | in the first line it is a header line
                if '|' not in l:
                    continue
            # Skip blank lines
            if not line:
                continue

            # Skip summary lines and set finished processing
            if line[0] == '=':
                finished = True
            if finished:
                break

            b = BlastResultRow( line )
            assert b != None
            assert b.ident
            yield b
        fh.close()

class BlastResultRow:
    def __init__( self, strline = None ):
        self.ident = ""
        self.genbankinfo = []
        self.match = 0
        self.other = []
        self.species = ""
        self.speciesid = -1
        self.genusname = ""
        self.genusid = -1

        self.rawline = strline.strip()

        self._setup()

        if strline:
            self._parse( strline )

    def _setup( self ):
        pattern = '([\w\s]+)?\s+\((\S?[0-9]+)\)'
        self.nameidp = re.compile( pattern )

    def _parse( self, line ):
        """
            Parse a single row in a blast result table
        """
        columns = line.split( '\t' )
        if not len( columns ) == 14:
            raise UnknownFormatException( "Blast row:\n%s\ndoes not contain exactly 14 columns" % line )
        self.ident = columns[0]
        self.genbankinfo = columns[1].split( '|' )[0:-1]
        self.match = columns[2]
        self.other = columns[3:12]
        self.species, self.speciesid = self._parse_nameid( columns[12] )
        self.genus, self.genusid = self._parse_nameid( columns[13] )

    def _parse_nameid( self, text ):
        """
            Given a tax/genus of the form some name (id)
            split into ('some name', id)
        """
        m = self.nameidp.search( text )
        name, id = m.groups()
        return name, int( id )

    def __str__( self ):
        return self.__unicode__()

    def __unicode__( self ):
        return "%s-%s-%s-%s-%s-%s-%s-%s" % (self.ident, self.genbankinfo, self.match, self.other, self.species, self.speciesid, self.genus, self.genusid)
