import os.path

# 454 Specific Constants
_454MAPPINGPROJECT = "454MappingProject.xml"
_454NEWBLERMETRICS = "454NewblerMetrics.txt"
_454MAPPINGPATH = "mapping"

# Lookup tables for codon change types
transition_table = [ 'AG', 'GA', 'CT', 'TC' ]
TRANSITION_TEXT = "TRANSITION"
transversion_table = [ 'AC', 'CA', 'AT', 'TA', 'GT', 'TG', 'GC', 'CG' ]
TRANSVERSION_TEXT = "TRANSVERSION"

# Nucleotide values
GAP = '-'
STOP = '*'

# Degenerate bases
DEGENERATE_NUCLEOTIDES = { 'B': ['C','G','T'], 'D': ['A','G','T'], 'H': ['A','C','T'], 'V': ['A','C','G'], 'K': ['G','T'], 'M': ['A','C'], 'N': ['A','T','C','G'], 'R': ['G','A'], 'S': ['C','G'], 'W': ['A','T'], 'Y': ['C', 'T'] }
