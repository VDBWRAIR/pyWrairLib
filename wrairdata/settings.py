import os.path
import stat
import logging

# Log level DEBUG, WARNING, INFO
LOG_LEVEL = logging.DEBUG 

# The main directory for NGS Data structure
NGSDATA_DIR = '/home/EIDRUdata/NGSData'

# Data Directories
READSBYSAMPLE_DIR = os.path.join( NGSDATA_DIR, 'ReadsBySample' )
PRIMER_DIR = os.path.join( NGSDATA_DIR, 'Primer' )
RAWDATA_DIR = os.path.join( NGSDATA_DIR, 'RawData' )
READDATA_DIR = os.path.join( NGSDATA_DIR, 'ReadData' )

# What platforms are supported
#  with the filename_patter for output as well as the match pattern for reading filenames
PLATFORMS = {
    'Sanger': {
        'filename_pattern': '%s__%s__%s__%s__%s__%s.%s',
        'filename_match_pattern': '^(?P<samplename>\w+?)__(?P<primer>\w+?)__Sanger__(?P<date>\w+)__(?P<virus>\w+)__(?P<gene>\w+)\.(?P<fileextension>\w+)$'
    },
    'Roche454': {
        'filename_pattern': '%s__%s__%s__%s.%s',
        'filename_match_pattern': '^(?P<samplename>\w+?)__(?P<midkey>\w+?)__(?P<date>\w+)__(?P<virus>\w+)\.(?P<fileextension>\w+)$'
    },
    'IonTorrent': {
        'filename_pattern': '%s__%s__%s__%s.%s',
        'filename_match_pattern': '^(?P<samplename>\w+?)__(?P<midkey>\w+?)__(?P<date>\w+)__(?P<virus>\w+)\.(?P<fileextension>\w+)$'
    }
}

'''
Default Ownership and Permissions
'''
OWNER = 603
GROUP = 499

'''
stat.S_IRWXU: Read, write, and execute by owner.
stat.S_IRUSR: Read by owner.
stat.S_IWUSR: Write by owner.
stat.S_IXUSR: Execute by owner.
stat.S_IRWXG: Read, write, and execute by group.
stat.S_IRGRP: Read by group.
stat.S_IWGRP: Write by group.
stat.S_IXGRP: Execute by group.
stat.S_IRWXO: Read, write, and execute by others.
stat.S_IROTH: Read by others.
stat.S_IWOTH: Write by others.
stat.S_IXOTH: Execute by others.
'''
PERMS = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
