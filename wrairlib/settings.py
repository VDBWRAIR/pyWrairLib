import os.path
import stat
import logging
import logging.config
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
LOG_LEVEL = getattr( logging, config['DEFAULT']['LOG_LEVEL'] )

def setup_logger( *args, **kwargs ):
    ''' Setup logging and return logger instance '''
    if 'name' not in kwargs:
        kwargs['name'] = args[0]

    logging_config = config['Logging']
    logging_config['version'] = int( logging_config['version'] )
    logging.config.dictConfig( config['Logging'] )
    logger = logging.getLogger( 'wrair.' + kwargs['name'] )

    return logger
