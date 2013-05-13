import os.path
import stat
import logging
import sys

from configobj import ConfigObj

def parse_config( pathtoconfig ):
    return ConfigObj( pathtoconfig, interpolation='Template' )

# Hack for testing to make sure the local settings.cfg is used not
# the installed one
if 'site-packages' in __file__:
    prefix = sys.prefix
else:
    prefix = os.path.dirname( os.path.dirname( __file__ ) )
path_to_config = os.path.join( prefix, 'config', 'settings.cfg' )

config = parse_config( path_to_config )

# Log level DEBUG, WARNING, INFO
LOG_LEVEL = getattr( logging, config['DEFAULT']['LOG_LEVEL'] )
