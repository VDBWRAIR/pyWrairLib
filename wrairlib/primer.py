# Do things with primer files
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import os
import os.path
import re
import glob

class PrimerRegion:
    """
        Defines a primer region which is composed of a start, end and direction
    """
    def __init__( self, start, end, direction ):
        self.start = start
        self.end = end
        self.direction = direction

    def __str__( self ):
        return "(%s, %s, '%s')" % (self.start, self.end, self.direction)

    def __unicode__( self ):
        return self.__str__()

    def __repr__( self ):
        return self.__str__()

    def __cmp__( self, other ):
        '''
            Defines how to compare two Primer regions

            Two primer regions are equal if and only if
            start, end and direction are the same
            >>> x = PrimerRegion( 1, 2, 'F' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> y == x
            True

            A primer region is less than another primer region
            based on a few different criteria
            Criteria one:
                Reverse direction is always greater than Forward
                This is to keep the Forward and Reverse regions
                segregated in sorting operations
            >>> x = PrimerRegion( 1, 2, 'R' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> x < y
            False
            >>> x > y
            True

            Criteria two:
                If both starts are equal 
                then end is compared to determine less than or greater than
            >>> x = PrimerRegion( 1, 3, 'F' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> x < y
            False
            >>> x > y
            True

            Criteria three:
                If start is greater than the right operand region
                then it is greater than otherwise it is less than
            >>> x = PrimerRegion( 2, 2, 'F' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> x < y
            False
            >>> x > y
            True
        '''
        if self.direction != other.direction:
            if self.direction.lower() == 'f':
                return -1
            else:
                return 1
        else:
            if self.start == other.start:
                if self.end < other.end:
                    return -1
                elif self.end > other.end:
                    return 1
                else:
                    return 0
            elif self.start < other.start:
                return -1
            elif self.start > other.start:
                return 1

    def __eq__( self, other ):
        '''
            Just use the hash function to determine equality
            __eq__ is used by the set data type to determine equality FYI
        '''
        return self.__hash__() == other.__hash__()

    def __hash__( self ):
        '''
            Return the hash of the string produced by concatting each of the 3 pieces of the Primer Region

            >>> x = PrimerRegion( 1, 2, 'F' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> y.__hash__() == x.__hash__()
            True
            >>> set( [x,y] ) == set( [x] )
            True
            >>> x = PrimerRegion( 1, 2, 'R' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> y.__hash__() == x.__hash__()
            False
            >>> x = PrimerRegion( 1, 3, 'F' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> y.__hash__() == x.__hash__()
            False
            >>> x = PrimerRegion( 2, 2, 'F' )
            >>> y = PrimerRegion( 1, 2, 'F' )
            >>> y.__hash__() == x.__hash__()
            False
            >>> set( [x, y] ) == set( [x, y] )
            True
        '''
        return ('%s%s%s' % (self.start,self.end,self.direction)).__hash__()

class Primer:
    def __init__( self, primerfile ):
        self.primerfile = primerfile

    def get_merged_primer_regions( self, strmatch ):
        """
            Remove duplicated regions due to degenerate bases

            >>> primers = glob.glob( 'Examples/Primer/*' )
            >>> for p in primers:
            ...  p
            ...  Primer( p ).get_merged_primer_regions( 'PB1' )
            'Examples/Primer/AH3N2_FDFusion_primer20120316.fna'
            [(474, 517, 'F'), (485, 530, 'F'), (900, 944, 'F'), (1036, 1079, 'F'), (1410, 1454, 'F'), (1860, 1903, 'F'), (484, 530, 'R'), (1100, 1145, 'R'), (1475, 1520, 'R'), (1625, 1668, 'R'), (2250, 2294, 'R')]
            'Examples/Primer/swH1N1_FD_primer_nodeg.fasta'
            [(299, 318, 'F'), (713, 734, 'F'), (834, 857, 'F'), (1735, 1757, 'F'), (312, 327, 'R'), (505, 521, 'R'), (805, 823, 'R'), (860, 882, 'R'), (1069, 1088, 'R'), (1517, 1539, 'R')]
            'Examples/Primer/H1N1_trim_prm.fna'
            [(1, 36, 'F'), (517, 557, 'F'), (1162, 1204, 'F'), (1664, 1701, 'F'), (599, 641, 'R'), (1231, 1274, 'R'), (1725, 1770, 'R')]
            'Examples/Primer/D3_FDFusion_HS.fna'
            []
        """
        pregions = self.get_primer_regions( strmatch )
    
        # Remove duplicates using set operation and then sort results returning a list
        return sorted( set( pregions ) )

    def get_primer_regions( self, strmatch ):
        """
            Get primer regions from all sequences for specified matching string in seq.id
            Returns regions for every primer even if they are duplicates
            Duplicates probably indicated that degenerate bases are included in the primer file
            You can use get_merged_primer_regions to remove these

            >>> primers = glob.glob( 'Examples/Primer/*' )
            >>> for p in primers:
            ...  p
            ...  Primer( p ).get_primer_regions( 'PB1' )
            'Examples/Primer/AH3N2_FDFusion_primer20120316.fna'
            [(474, 517, 'F'), (485, 530, 'F'), (900, 944, 'F'), (1036, 1079, 'F'), (1410, 1454, 'F'), (1860, 1903, 'F'), (484, 530, 'R'), (1100, 1145, 'R'), (1475, 1520, 'R'), (1475, 1520, 'R'), (1625, 1668, 'R'), (2250, 2294, 'R')]
            'Examples/Primer/swH1N1_FD_primer_nodeg.fasta'
            [(299, 318, 'F'), (713, 734, 'F'), (834, 857, 'F'), (1735, 1757, 'F'), (312, 327, 'R'), (505, 521, 'R'), (805, 823, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (860, 882, 'R'), (1069, 1088, 'R'), (1517, 1539, 'R')]
            'Examples/Primer/H1N1_trim_prm.fna'
            [(1, 36, 'F'), (517, 557, 'F'), (1162, 1204, 'F'), (1664, 1701, 'F'), (599, 641, 'R'), (1231, 1274, 'R'), (1725, 1770, 'R')]
            'Examples/Primer/D3_FDFusion_HS.fna'
            []
        """
        regions = []
        try:
            for seq in SeqIO.parse( self.primerfile, 'fasta' ):
                if strmatch in seq.id:
                    regions.append( self.get_region_from_sequence( seq ) )
        except IOError as e:
            # I just want to awknowledge that this could be there
            raise e

        # Sort
        regions.sort( )

        return regions

    def get_region_from_sequence( self, sequence, pattern = None ):
        """
            Return a PrimerRegion representing the Position, start and end of the given
            Bio.seq object

            Start and end are dependent on the Direction of the primer and the name of the primer

            The initial point is determined by doing a regular expression match using the pattern argument if given
            otherwise it will search the seq.id field of the given sequence for any terms such as:
                F or R followed by underscore or dash followed by any amount of numbers
                    -- or --
                any ammount of numbers followed by any uppercase letters followed by R or F

            Once the initial point is deteremined the direction is pulled from that same search
            If the direction is Reverse then the initial point is the End of the region otherwise it is the Start
            If the end was discovered then the start is set using sequence end - sequence length
             otherwise the end is set using start + sequence length

            >>> p = Primer( 'somefile' )
            >>> primers = []
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_F_741M'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_R_741M'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_F741M'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_R741M'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_F-741M'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_R-741M'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_741MF'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_741MR'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_741F'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>PB2_H3N2_741R'
            >>> primers.append( SeqRecord( Seq( 'AAAAAAAAAA' ) ) )
            >>> primers[-1].id = '>Junk_FD_12'
            >>> for pr in primers:
            ...  print p.get_region_from_sequence( pr )
            (741, 751, 'F')
            (731, 741, 'R')
            (741, 751, 'F')
            (731, 741, 'R')
            (741, 751, 'F')
            (731, 741, 'R')
            (741, 751, 'F')
            (731, 741, 'R')
            (741, 751, 'F')
            (731, 741, 'R')
            None
        """
        if pattern is None:
            pattern = '(?:(R|F)_*-*([0-9]+)|([0-9]+)[A-Z]*(R|F))'

        dpos = re.search( pattern, sequence.id )

        # Return None if no match was made
        if dpos is None:
            return None
        else:
            dpos = list( dpos.groups() )

        # Remove None values
        # Sort so that F & R are always second element
        dpos = sorted( filter( lambda x: x is not None, dpos ) )
        
        # Lets just be really sure :)
        assert dpos[1] in 'FRfr'
    
        try:
            dpos[0] = int( dpos[0] )
        except ValueError as e:
            sys.stderr.write( "Error while parsing primer identifier %s.\nCould not convert %s to integer\n" % (sequence.id, dpos[0] ) )
        # Deal with the sequence length now to complete the region
        seqlen = len( str( sequence.seq ) )
        # If Forward primer then the position is the start
        # and have to place an end
        if dpos[1].lower() == 'f':
            dpos.insert( 1, dpos[0] + seqlen )
        else:
            # If Reverse primer then the position is the end
            # and have to place the start
            dpos.insert( 0, dpos[0] - seqlen )
            
        return PrimerRegion( *dpos )


if __name__ == '__main__':
    import doctest
    doctest.testmod()
