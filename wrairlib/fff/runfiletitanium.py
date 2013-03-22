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
                count += 1
                continue
            elif count == 1:
                self.regions, self.type = self._parse_regions_line( row )
            elif count == 2:
                stuff = self._parse_id_line( row )
                self.id = stuff['id']
                self.date = date( int(stuff['date'][4:]), int(stuff['date'][:2]), int(stuff['date'][2:4]) )
            elif row.startswith( '#' ):
                count += 1
                continue
            else:
                self.samples.append( RunFileSample( row.strip(), self ) )
            count += 1

    def _parse_id_line( self, line ):
        """
            Parse Run File Id line # Run File ID: \S+

            >>> import re
            >>> line = "# Run File ID: 12232011.AFRIMS_Den2AndPathogenDiscovery"
            >>> mc = re.compile( "# Run File ID: (?P<date>\d{2}\d{2}\d{4}).(?P<id>\S+)" )
            >>> m = mc.match( line )
            >>> assert m.groupdict() == { 'date': '12232011', 'id': 'AFRIMS_Den2AndPathogenDiscovery' }
            >>> line = "# Run File ID: 03122013.RAN_PHAGEandFluA_Universal"
            >>> m = mc.match( line )
            >>> assert m.groupdict() == { 'date': '03122013', 'id': 'RAN_PHAGEandFluA_Universal' }
        """
        m = re.match( "# Run File ID: (?P<date>\d{2}\d{2}\d{4}).(?P<id>\S+)", line )
        if not m:
            raise ValueError( "Unkown Run File ID line -->%s" % line )
        return m.groupdict()

    def _parse_regions_line( self, line ):
        """
            Parse Region line # [0-9] \w+ \w+
        
            >>> line = "# 2 Region PTP".split()
            >>> assert len( line ) == 4
            >>> assert len( [int(i) for i in range( 1, int(line[1]) + 1 )] ) == 2
        """
        s = line.strip().split( )
        try:
            regions = [int(i) for i in range( 1, int(s[1]) + 1 )]
            rftype = s[3]
        except IndexError as e:
            print line
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

        # Check for comment character
        if s[0].startswith( '#' ):
            self.disabled = True
            self.region = int( s[0][1:] )
        else:
            self.region = int( s[0] )
        self.name = s[1]
        self.genotype = s[2]
        self.midkeyname = s[3]
        self.mismatchtolerance = int( s[4] )
        if s[5] == 'VOID' or s[5] == 'User_defined_Reference':
            self.refgenomelocation = None
        else:
            self.refgenomelocation = s[5]
        self.uniquesampleid = s[6]
        if s[7] == 'VOID' or s[7] == 'User_defined_Primer':
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
