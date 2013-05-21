""" Represents a RunFile Titanium and hopefully listFiles for Valmik's Pipeline """

import re
from datetime import date
from wrairnaming import Formatter

from StringIO import StringIO

class RunFile( object ):
    def __init__( self, handle ):
        """
            Set the handle to the RunFile
        """
        if isinstance( handle, str ):
            handle = open( handle )
        self.handle = handle
        self.regions = []
        self.id = ""
        self._samples = []
        self.samples_by_region = {}
        self.headers = []
        self._parse()

    @property
    def samples( self ):
        '''
            Return a list of all items joined together from the regions dictionary
        '''
        return [sample for r, samples in self.samples_by_region.items() for mid, sample in samples.items()]

    def __getitem__( self, key ):
        ''' Should return list of samples for a given region '''
        return self.samples_by_region[key]

    def add_sample( self, rfsample ):
        if rfsample.region not in self.samples_by_region:
            self.samples_by_region[rfsample.region] = {}
        self.samples_by_region[rfsample.region][rfsample.midkeyname] = rfsample

    def _parse( self ):
        """
            Parse the file into the important pieces
        """
        count = 0
        for row in self.handle:
            # Get the headers
            if row.startswith( '!' ):
                self.headers = row[1:].split( '\t' )
            elif count == 0:
                self.platform = row[2:].split()[0]
                count += 1
                continue
            elif count == 1:
                self.regions, self.type = self._parse_regions_line( row )
            elif count == 2:
                stuff = self._parse_id_line( row )
                self.id = stuff['id']
                self.date = stuff['date']
            elif row.startswith( '#' ):
                count += 1
                continue
            else:
                self.add_sample( RunFileSample( row.strip(), self ) )
            count += 1
        # Empty runfile
        # Hack for testing: allows StringIO to be empty
        if count == 0 and not isinstance( self.handle, StringIO ):
            raise ValueError( "Empty Runfile" )

    def _parse_id_line( self, line ):
        """
            Parse Run File Id line # Run File ID: \S+

        """
        m = re.match( "# Run File ID: (\d{2})(\d{2})(\d{4}).(\S+)", line )
        if not m:
            raise ValueError( "Unkown Run File ID line -->%s" % line )
        pieces = m.groups()
        info = {}
        # This will raise ValueError if parts are incorrect
        info['date'] = date( int(pieces[2]), int(pieces[0]), int(pieces[1]) )
        info['id'] = pieces[3]
        return info

    def _parse_regions_line( self, line ):
        """
            Parse Region line # [0-9] \w+ \w+
        """
        m = re.match( '# (\d+) Region (.*)$', line )
        if not m:
            raise ValueError( "Unparsable region line: '%s'" % line )
        m = m.groups()

        # Create a tuple of regions
        regions = int( m[0] )
        if regions == 0:
            raise ValueError( "0 is not a valid amount of regions" )
        regions = tuple( range( 1, regions + 1) )

        # The Region Type
        rftype = m[1]

        return regions, rftype

class RunFileSample:
    def __init__( self, runfilerow, runfile ):
        self.runfilerow = runfilerow
        self.disabled = False
        self._parse_sample_row( runfilerow )
        self.runfile = runfile

    def _parse_row( self, row ):
        if row.startswith( '!' ):
            raise ValueError( "Got header row from RunFile" )

    def _parse_sample_row( self, row ):
        r"""
            Parse the given row and set
            instance properties

            >>> rfs = RunFileSample( '1\tKDC0119A\tDengue2\tTI-MID1\t1\tVOID\tKDC0119A\tVOID', None )
            >>> assert rfs.region == 1
            >>> assert rfs.name == 'KDC0119A'
            >>> assert rfs.genotype == 'Dengue2'
            >>> assert rfs.midkeyname == 'TI-MID1'
            >>> assert rfs.mismatchtolerance == 1
            >>> assert rfs.refgenomelocation == None
            >>> assert rfs.uniquesampleid == 'KDC0119A'
            >>> assert rfs.primers == None
            >>> assert rfs.disabled == False

            >>> rfs = RunFileSample( '#1\tKDC0119A\tDengue2\tTI-MID1\t1\tVOID\tKDC0119A\tVOID', None )
            >>> assert rfs.region == 1
            >>> assert rfs.name == 'KDC0119A'
            >>> assert rfs.genotype == 'Dengue2'
            >>> assert rfs.midkeyname == 'TI-MID1'
            >>> assert rfs.mismatchtolerance == 1
            >>> assert rfs.refgenomelocation == None
            >>> assert rfs.uniquesampleid == 'KDC0119A'
            >>> assert rfs.primers == None
            >>> assert rfs.disabled == True
        """
        # Should be tab delimeted
        s = row.split( '\t' )

        if len( s ) != 8:
            raise ValueError( "Sample Row does not contain all necessary columns: %s" % s )

        # Check for comment character
        if s[0].startswith( '#' ):
            self.disabled = True
            self.region = int( s[0][1:] )
        else:
            self.region = int( s[0] )
        self.name = s[1]
        self.genotype = s[2]
        self.midkeyname = s[3]
        if s[4] == '':
            self.mismatchtolerance = 0
        else:
            try:
                self.mismatchtolerance = int( s[4] )
            except ValueError as e:
                raise ValueError( "Invalid mismatch tolerance given: %s" % s[4] )
        if s[5].upper() == 'VOID' or 'user_defined' in s[5].lower():
            self.refgenomelocation = None
        else:
            self.refgenomelocation = s[5]
        self.uniquesampleid = s[6]
        if s[7].upper() == 'VOID' or 'user_defined' in s[7].lower() or s[7] == '':
            self.primers = None
        else:
            self.primers = s[7]

    def __str__( self ):
        return self.runfilerow

    def __unicode__( self ):
        return self.__str__()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
