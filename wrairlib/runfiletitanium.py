""" Represents a RunFile Titanium and hopefully listFiles for Valmik's Pipeline """

import re
from datetime import date

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
        self.samples = []
        self.headers = []
        self._parse()

    def _parse( self ):
        """
            Parse the file into the important pieces

            >>> rf = RunFile( open( '/home/EIDRUdata/Data_seq454/2011_12_23/D_2011_12_24_00_58_20_vnode_signalProcessing/RunfileTitanium_122311.txt' ) )
            >>> assert rf.type == 'PTP'
            >>> assert rf.platform == 'Roche454'
            >>> assert rf.regions == [1,2]
            >>> assert rf.id == 'AFRIMS_Den2AndPathogenDiscovery'
            >>> assert rf.date == date( 2011, 12, 23 )
            >>> assert len( rf.headers ) == 8
            >>> assert len( rf.samples ) == 66
            >>> rf = RunFile( open( '/home/EIDRUdata/NGSData/ReadData/Roche454/D_2013_03_13_13_56_26_vnode_signalProcessing/meta/Runfile__FlxPlus__2013_03_12.txt' ) )
            >>> assert rf.type == 'PTP'
            >>> assert rf.regions == [1,2]
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
                self.samples.append( RunFileSample( row.strip(), self ) )
            count += 1

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
        if s[5] == 'VOID' or s[5] == 'User_defined_Reference':
            self.refgenomelocation = None
        else:
            self.refgenomelocation = s[5]
        self.uniquesampleid = s[6]
        if s[7] == 'VOID' or s[7] == 'User_defined_Primer' or s[7] == '':
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
