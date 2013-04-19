# Do things with primer files
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import os
import os.path
import re
import glob
import sys

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
    '''
            >>> primers = glob.glob( 'Examples/Primer/*' )
            >>> for p in primers:
            ...  p
            ...  primer = Primer( p )
            ...  for gene in primer.unique_genes( ):
            ...    gene
            ...    primer.get_merged_primer_regions( gene )
            'Examples/Primer/AH3N2_FDFusion_primer20120316.fna'
            'HA'
            [(1, 38, 'F'), (2, 44, 'F'), (453, 495, 'F'), (816, 860, 'F'), (872, 916, 'F'), (1210, 1256, 'F'), (546, 589, 'R'), (931, 975, 'R'), (1278, 1323, 'R'), (1378, 1425, 'R')]
            'PB1'
            [(474, 517, 'F'), (485, 530, 'F'), (900, 944, 'F'), (1036, 1079, 'F'), (1410, 1454, 'F'), (1860, 1903, 'F'), (484, 530, 'R'), (1100, 1145, 'R'), (1475, 1520, 'R'), (1625, 1668, 'R'), (2250, 2294, 'R')]
            'PB2'
            [(452, 495, 'F'), (741, 784, 'F'), (953, 997, 'F'), (1426, 1469, 'F'), (1475, 1519, 'F'), (1747, 1793, 'F'), (525, 569, 'R'), (1085, 1126, 'R'), (1457, 1502, 'R'), (1553, 1595, 'R'), (2022, 2067, 'R'), (2296, 2341, 'R')]
            'NA'
            [(415, 459, 'F'), (880, 922, 'F'), (905, 951, 'F'), (1100, 1143, 'F'), (517, 560, 'R'), (683, 726, 'R'), (942, 984, 'R'), (1047, 1090, 'R'), (1397, 1444, 'R')]
            'PA'
            [(86, 131, 'F'), (387, 431, 'F'), (455, 501, 'F'), (718, 762, 'F'), (931, 977, 'F'), (1123, 1165, 'F'), (1763, 1806, 'F'), (520, 564, 'R'), (743, 787, 'R'), (915, 965, 'R'), (1341, 1384, 'R'), (1457, 1503, 'R'), (1867, 1909, 'R'), (2166, 2212, 'R')]
            'MP'
            [(245, 287, 'F'), (359, 402, 'F'), (478, 520, 'F'), (509, 553, 'R'), (887, 928, 'R')]
            'NP'
            [(1, 37, 'F'), (518, 562, 'F'), (1042, 1086, 'F'), (621, 665, 'R'), (1106, 1152, 'R')]
            'NS'
            [(44, 87, 'F'), (427, 470, 'F'), (477, 520, 'R'), (770, 813, 'R')]
            'Examples/Primer/swH1N1_FD_primer_nodeg.fasta'
            'NS'
            [(65, 88, 'F'), (212, 230, 'F'), (245, 267, 'F'), (287, 310, 'F'), (528, 547, 'F'), (642, 660, 'F'), (298, 316, 'R'), (533, 553, 'R'), (596, 619, 'R'), (680, 696, 'R'), (743, 766, 'R'), (819, 838, 'R')]
            'PB1'
            [(299, 318, 'F'), (713, 734, 'F'), (834, 857, 'F'), (1735, 1757, 'F'), (312, 327, 'R'), (505, 521, 'R'), (805, 823, 'R'), (860, 882, 'R'), (1069, 1088, 'R'), (1517, 1539, 'R')]
            'PB2'
            [(168, 188, 'F'), (200, 217, 'F'), (555, 578, 'F'), (726, 742, 'F'), (1241, 1258, 'F'), (1244, 1264, 'F'), (1722, 1740, 'F'), (2058, 2074, 'F'), (282, 303, 'R'), (774, 799, 'R'), (1187, 1210, 'R'), (1324, 1347, 'R'), (1738, 1761, 'R'), (1839, 1856, 'R'), (2094, 2115, 'R'), (2157, 2180, 'R')]
            'NA'
            [(133, 156, 'F'), (475, 498, 'F'), (540, 561, 'F'), (918, 939, 'F'), (940, 960, 'F'), (1307, 1326, 'F'), (230, 252, 'R'), (556, 576, 'R'), (574, 591, 'R'), (967, 988, 'R'), (1286, 1309, 'R'), (1455, 1475, 'R')]
            'PA'
            [(144, 162, 'F'), (214, 231, 'F'), (573, 592, 'F'), (873, 893, 'F'), (922, 944, 'F'), (1385, 1403, 'F'), (1482, 1501, 'F'), (1978, 1995, 'F'), (315, 333, 'R'), (602, 626, 'R'), (859, 882, 'R'), (943, 964, 'R'), (1471, 1490, 'R'), (1708, 1731, 'R'), (1809, 1828, 'R'), (2019, 2042, 'R')]
            'FD'
            []
            'MP'
            [(202, 221, 'F'), (390, 408, 'F'), (450, 473, 'F'), (553, 571, 'F'), (788, 809, 'F'), (262, 280, 'R'), (471, 491, 'R'), (605, 624, 'R'), (797, 815, 'R'), (876, 897, 'R'), (949, 972, 'R')]
            'NP'
            [(54, 75, 'F'), (208, 228, 'F'), (543, 560, 'F'), (603, 626, 'F'), (798, 821, 'F'), (1050, 1069, 'F'), (1370, 1391, 'F'), (287, 303, 'R'), (634, 654, 'R'), (720, 743, 'R'), (1112, 1133, 'R'), (1370, 1387, 'R'), (1530, 1549, 'R')]
            'HA'
            [(34, 57, 'F'), (84, 105, 'F'), (313, 336, 'F'), (373, 395, 'F'), (1119, 1136, 'F'), (1265, 1285, 'F'), (1469, 1488, 'F'), (467, 490, 'R'), (547, 571, 'R'), (602, 625, 'R'), (1123, 1142, 'R'), (1197, 1217, 'R'), (1574, 1593, 'R'), (1678, 1701, 'R')]
            'Examples/Primer/H1N1_trim_prm.fna'
            'NS'
            [(414, 453, 'F'), (528, 567, 'F'), (608, 650, 'R'), (831, 872, 'R')]
            'PB1'
            [(1, 36, 'F'), (517, 557, 'F'), (1162, 1204, 'F'), (1664, 1701, 'F'), (599, 641, 'R'), (1231, 1274, 'R'), (1725, 1770, 'R')]
            'PB2'
            [(394, 433, 'F'), (1010, 1051, 'F'), (1653, 1693, 'F'), (615, 658, 'R'), (1072, 1111, 'R'), (1716, 1761, 'R')]
            'NA'
            [(546, 584, 'F'), (906, 944, 'F'), (622, 665, 'R'), (977, 1018, 'R')]
            'PA'
            [(500, 540, 'F'), (1033, 1070, 'F'), (1736, 1774, 'F'), (618, 659, 'R'), (1106, 1147, 'R'), (1749, 1790, 'R')]
            'MP'
            [(542, 582, 'F'), (608, 649, 'R')]
            'NP'
            [(489, 527, 'F'), (1033, 1071, 'F'), (596, 640, 'R'), (1095, 1135, 'R')]
            'HA'
            [(380, 419, 'F'), (840, 878, 'F'), (1250, 1288, 'F'), (593, 635, 'R'), (897, 937, 'R'), (1310, 1353, 'R')]
            'Examples/Primer/D3_FDFusion_HS.fna'
            'AADen3'
            [(37, 79, 'F'), (297, 342, 'F'), (766, 807, 'F'), (1305, 1346, 'F'), (1919, 1959, 'F'), (2385, 2424, 'F'), (2902, 2944, 'F'), (3528, 3567, 'F'), (3953, 3997, 'F'), (4358, 4401, 'F'), (4552, 4595, 'F'), (4939, 4979, 'F'), (5400, 5447, 'F'), (5888, 5932, 'F'), (6187, 6229, 'F'), (6523, 6569, 'F'), (6912, 6953, 'F'), (7373, 7411, 'F'), (7808, 7848, 'F'), (8291, 8335, 'F'), (8573, 8614, 'F'), (8870, 8911, 'F'), (9195, 9238, 'F'), (9496, 9535, 'F'), (9860, 9899, 'F'), (10173, 10213, 'F'), (10469, 10508, 'F'), (342, 383, 'R'), (454, 495, 'R'), (1451, 1495, 'R'), (2093, 2133, 'R'), (2565, 2607, 'R'), (3114, 3158, 'R'), (3699, 3740, 'R'), (4036, 4079, 'R'), (4682, 4721, 'R'), (5002, 5043, 'R'), (5520, 5562, 'R'), (5944, 5990, 'R'), (6214, 6260, 'R'), (6695, 6739, 'R'), (7437, 7481, 'R'), (7917, 7959, 'R'), (8408, 8449, 'R'), (8967, 9011, 'R'), (9264, 9307, 'R'), (9658, 9698, 'R'), (10006, 10048, 'R'), (10394, 10433, 'R'), (10657, 10699, 'R')]
    '''
    def __init__( self, primerfile ):
        self.primerfile = primerfile

    def unique_genes( self, pattern=None ):
        """
            Return the unique set of gene names from primer file
            By default search every seq.id field for ([a-zA-Z0-9]+)(?:[_-]))

            The search pattern should have only 1 group that is returned

            >>> primers = glob.glob( 'Examples/Primer/*' )
            >>> for p in primers:
            ...  p
            ...  Primer( p ).unique_genes( )
            'Examples/Primer/AH3N2_FDFusion_primer20120316.fna'
            set(['HA', 'PB1', 'PB2', 'NA', 'PA', 'MP', 'NP', 'NS'])
            'Examples/Primer/swH1N1_FD_primer_nodeg.fasta'
            set(['NS', 'PB1', 'PB2', 'NA', 'PA', 'FD', 'MP', 'NP', 'HA'])
            'Examples/Primer/H1N1_trim_prm.fna'
            set(['NS', 'PB1', 'PB2', 'NA', 'PA', 'MP', 'NP', 'HA'])
            'Examples/Primer/D3_FDFusion_HS.fna'
            set(['AADen3'])
        """
        if pattern is None:
            pattern = '([a-zA-Z0-9]+)(?:[_-])'

        # Use set as we only want unique
        genes = set()
        cp = re.compile( pattern )
        with open( self.primerfile ) as fh:
            for line in fh:
                if line.startswith( '>' ):
                    m = cp.search( line )
                    if m:
                        genes.add( m.groups()[0] )
                    else:
                        raise ValueError( "%s did not match identifier %s" % (pattern, line.strip() ) )
        return genes

    def get_search_for_pattern( self, pattern, string ):
        """ Generic function to return match from pattern """
        if type( pattern ) == str:
            pattern = re.compile( pattern )
        return pattern.search( string )
        

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
                    try:
                        regions.append( self.get_region_from_sequence( seq ) )
                    except ValueError as e:
                        # Skip malformed lines
                        sys.stderr.write( "Could not parse %s because %s" % (seq.id, str(e)) )
                        continue
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
            ...  try:
            ...   print p.get_region_from_sequence( pr )
            ...  except ValueError as e:
            ...   print "Caught"
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
            Caught
        """
        if pattern is None:
            pattern = '(?:(R|F)_*-*([0-9]+)|([0-9]+)[A-Z]*(R|F))'

        dpos = re.search( pattern, sequence.id )

        # Return None if no match was made
        if dpos is None:
            raise ValueError( "Error while parsing primer identifier %s" % sequence.id )
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
            raise ValueError( "Error while parsing primer identifier %s.\nCould not convert %s to integer\n" % (sequence.id, dpos[0] ) )
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
