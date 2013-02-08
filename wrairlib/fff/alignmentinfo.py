import sys

class BadFormatException( Exception ):
    def __init__( self, error ):
        self.error = error
    def __str__( self ):
        return self.error

class AlignmentInfo(object):
    """ Parse 454AlignmentInfo.tsv """
    def __init__( self, filepath ):
        """
            >>> ai = AlignmentInfo( 'examples/05_11_2012_1_TI-MID10_PR_2357_AH3/mapping/454AlignmentInfo.tsv' )
            >>> len( ai.seqs )
            37
        """
        self.seqs = []
        self._parse( filepath )

    def _parse( self, filepath ):
        fh = open( filepath )
        seqalign = None
        for line in fh:
            line = line.strip()
            if line.startswith( 'Position' ):
                continue
            elif line.startswith( '>' ):
                # If previously had data then create SeqAlignment object
                if seqalign:
                    self.seqs.append( SeqAlignment( seqalign ) )
                seqalign = []
                seqalign.append( line )
            elif line[0] in "123456789":
                seqalign.append( line )
            else:
                raise BadFormatException( "%s has incorrect format in line %s" % (filepath, line) )
        self.seqs.append( SeqAlignment( seqalign ) )
        fh.close()

class SeqAlignment( object ):
    """ Represents a single sequence alignment """
    def __init__( self, seqalignment ):
        """
            >>> seqalign = [\
            '>SeqID1\t1',\
            '1\tA\tA\t1\t1\t1\t1\t1.1\t1.1',\
            '2\tB\t-\t4\t1\t1\t1\t1.3\t1.3',\
            '2\tC\t-\t4\t1\t1\t1\t1.3\t1.3',\
            '3\tD\t-\t4\t1\t1\t1\t1.3\t1.3',\
            '5\tE\t-\t4\t1\t1\t1\t1.3\t1.3',\
            '8\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            '9\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            '10\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            '11\tE\t-\t4\t1\t9\t11\t1.3\t1.3',\
            '12\tE\t-\t4\t1\t8\t11\t1.3\t1.3',\
            '14\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            '14\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            '15\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            '16\tE\t-\t4\t1\t11\t11\t1.3\t1.3',\
            ]
            >>> s = SeqAlignment( seqalign )
            >>> s.name
            'SeqID1'
            >>> len( s.bases )
            18
            >>> s.bases[4].pos
            4
            >>> s.bases[4].gapType
            0
            >>> len( s.regions )
            8
            >>> print s.regions[0]
            Region between bases 1 and 3 is LowCoverage
            >>> print s.regions[-1]
            Region between bases 14 and 16 is Normal
            >>> seqalign = [\
            '>SeqID1\t5',\
            '5\tE\t-\t4\t1\t1\t1\t1.3\t1.3',\
            '8\tE\t-\t4\t1\t1\t1\t1.3\t1.3',\
            '9\tE\t-\t4\t1\t1\t1\t1.3\t1.3',\
            ]
            >>> s = SeqAlignment( seqalign )
            >>> len( s.bases )
            9
            >>> len( s.regions )
            4
            >>> print s.regions[0]
            Region between bases 1 and 4 is Gap
        """
        self.bases = []
        self.regions = []
        self.name, self.astart = seqalignment[0].split()
        self.name = self.name[1:]
        self.astart = int( self.astart )
        self._parse( seqalignment[1:] )

    def _parse( self, seqalignment ):
        lastPos = self.astart - 1
        # Create coverage region for beginning
        # and add gap bases
        if lastPos != 0:
            for i in range( 1, self.astart ):
                self.bases.append( BaseInfo.gapBase( i ) )
            self.regions.append( CoverageRegion( 1, lastPos, 0 ) )

        # Start a new region beginning with the first base
        basei = BaseInfo( seqalignment[0] )
        self.regions.append( CoverageRegion( basei.pos, basei.pos, basei.gapType ) )

        for line in seqalignment:
            basei = BaseInfo( line )
            # Homopolomer or indel
            if basei.pos == lastPos:
                # Just set last pos so no gap while loop
                lastPos = basei.pos - 1
            # Insert gap bases
            if lastPos + 1 != basei.pos:
                # End old region
                self.regions[-1].end = lastPos
                # Start new gap region
                self.regions.append( CoverageRegion( lastPos + 1, lastPos + 1, 0 ) )
                while lastPos + 1 != basei.pos:
                    lastPos += 1
                    self.bases.append( BaseInfo.gapBase( lastPos ) )
                # End gap region
                self.regions[-1].end = lastPos
                # Start new region
                self.regions.append( CoverageRegion( basei.pos, basei.pos, basei.gapType ) )

            # This base has different region type than current region
            if basei.gapType != self.regions[-1].rtype:
                self.regions[-1].end = lastPos
                self.regions.append( CoverageRegion( basei.pos, basei.pos, basei.gapType ) )

            self.bases.append( basei )
            lastPos = basei.pos

        # end current region
        self.regions[-1].end = lastPos

class CoverageRegion( object ):
    """ Store information about a region """
    def __init__( self, start, end, rtype = 1 ):
        self.start = start
        self.end = end
        # This should be "-1 -> LC, 0 -> GAP or 1 -> BASE"
        self.rtype = rtype

    @property
    def regionType( self ):
        if self.rtype == -1:
            return 'LowCoverage'
        if self.rtype == 0:
            return 'Gap'
        if self.rtype == 1:
            return 'Normal'

    def __unicode__( self ):
        return self.__str__()

    def __str__( self ):
        return "Region between bases %s and %s is %s" % (self.start, self.end, self.regionType)

class BaseInfo( object ):
    @staticmethod
    def gapBase( pos ):
        bi = BaseInfo( "%s\t-\t-\t64\t1\t1000\t1000\t0.0\t0.0" % pos )
        bi.gapType = 0
        return bi

    """ Represents a single base in an alignment """
    def __init__( self, seqalignline, lowcovcalc = None ):
        """
            Can feed whole line split up or just the line as a whole

            >>> lines = [\
            '689\tA\tA\t18\t1\t1\t1\t1.16\t1.16',\
            '734\tC\tC\t24\t1\t1\t1\t0.73\t0.73',\
            '1\t2'\
            ]
            >>> for line in lines:
            ...   try:
            ...     b = BaseInfo( line )
            ...     b.pos
            ...   except BadFormatException:
            ...     print 'Exception'
            689
            734
            Exception
        """
        if lowcovcalc is None:
            self.lcc = LowCoverageCalc

        cols = seqalignline.split( )
        alen = len( cols )
        if alen == 9:
            self.pos, self.refb, self.consb, \
            self.qual, self.udepth, self.adepth, \
            self.tdepth, self.signal, self.stddev = cols
        elif alen == 7:
            self.pos, self.consb, \
            self.qual, self.udepth, self.adepth, \
            self.signal, self.stddev = cols
        else:
            raise BadFormatException( "Incorrect amount of columns in %s" % seqalignline )

        # Determine type of base
        self.gapType = 1
        if self.lcc.isLowCoverage( self ):
            # LC = -1, Gap = 0, Normal = 1
            self.gapType = -1

    def __getattr__( self, obj, type = None ):
        return object.__getattr__( self, obj, type )

    def __setattr__( self, name, value ):
        """ Do some python magic to auto determine value type """
        try:
            if type( value ) == str and '.' in value:
                storeval = float( value )
            else:
                storeval = int( value )
        except (TypeError, ValueError):
            storeval = value
        object.__setattr__( self, name, storeval )

class LowCoverageCalc( object ):
    # Less than these numbers
    lowReadThreshold = 10

    @staticmethod
    def isLowCoverage( baseinfo ):
        """
            >>> bi = BaseInfo( "1\tA\tA\t18\t18\t18\t18\t1.0\t0.01" )
            >>> print LowCoverageCalc.isLowCoverage( bi )
            False
            >>> bi = BaseInfo( "1\tA\tA\t18\t18\t1\t1\t1.0\t0.01" )
            >>> print LowCoverageCalc.isLowCoverage( bi )
            True
        """
        if LowCoverageCalc.lowReadThreshold > baseinfo.adepth:
            return True
        else:
            return False

if __name__ == '__main__':
    import doctest
    doctest.testmod()
