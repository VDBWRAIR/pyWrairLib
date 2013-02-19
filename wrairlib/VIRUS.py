##########################################################################
##                       VIRUS
##	Author: Tyghe Vallard						                        
##	Date: 6/5/2012							                            
##	Version: 1.0							                            
##	Description:							                            
##      This script defines the different viruses at WRAIR
##      
#########################################################################
VIRUS_ALIASES = { 'AH3': ['H3N2'] }

#cat midkey_directories.index | sed 's/.*_\(\w\+\)$/\1/' | grep -v '^/' | sort | uniq > types
# Mapping from commonly seen names to normalized name for all virus types
# The key should be all lowercase to make the search easier(can just do VIRUS_LOOKUP[str.lower()] to match)
VIRUS_LOOKUP = {
    'acinetobactor': 'Acinetobactor',
    'ah1n1': 'sH1N1',
    'ah3': 'H3N2',
    'ah3n2': 'H3N2',
    'bacteria': 'bacteria',
    'bacteriophage': 'Bacteriophage',
    'bartonella': 'Bartonella',
    'coli': 'Ecoli',
    'dengue1': 'Dengue1',
    'dengue2': 'Dengue2',
    'dengue3': 'Dengue3',
    'dengue4': 'Dengue4',
    'denv1': 'Dengue1',
    'denv2': 'Dengue2',
    'ecoli': 'Ecoli',
    'flu': 'FluB',
    'flub': 'FluB',
    'h1n1': 'sH1N1',
    'h3n2': 'H3N2',
    'h5n1': 'H5N1',
    'infb': 'FluB',
    'infb': 'FluB',
    'influb': 'FluB',
    'malaria': 'Malaria',
    'ph1n1': 'pH1N1',
    'ph1n2': 'pH1N2',
    'ph1n3': 'pH1N3',
    'ph1n4': 'pH1N4',
    'phage': 'Phage',
    'rhinovirus': 'RHINOVIRUS',
    'seasonalh1n1': 'sH1N1',
    'seasonalh3n2': 'H3N2',
    'swah1n1': 'pH1N1',
    'swh1n1': 'pH1N1',
    'unknown': 'Unknown',
    'untyped': 'Unknown',
    'void': 'Unknown',
    'den1': 'Dengue1',
    'den2': 'Dengue2',
    'den3': 'Dengue3',
    'den4': 'Dengue4',
}
