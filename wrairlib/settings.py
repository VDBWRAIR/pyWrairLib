import os.path
import stat
import logging
import logging.config
import sys

from configobj import ConfigObj

# Hack for testing to make sure the local settings.cfg is used not
# the installed one
if 'site-packages' in __file__:
    prefix = sys.prefix
else:
    prefix = os.path.dirname( os.path.dirname( __file__ ) )
path_to_config = os.path.join( prefix, 'config', 'settings.cfg' )

def parse_config( pathtoconfig=path_to_config ):
    return ConfigObj( pathtoconfig, interpolation='Template' )

config = parse_config( path_to_config )
try:
    LOG_LEVEL = getattr( logging, config['DEFAULT']['LOG_LEVEL'] )
except KeyError as e:
    # Maybe DEFAULT or LOG_LEVEL was removed from config?
    sys.stderr.write( "Config file {} does not have a section named DEFAULT that " \
        "contains a subsection LOG_LEVEL\n".format( path_to_config ) )
    sys.stderr.write( "prefix for install is {}\n".format( prefix ) )
    sys.stderr.write( "script path is {}\n".format( __file__ ) )
    sys.exit( 1 )

def setup_logger( *args, **kwargs ):
    ''' Setup logging and return logger instance '''
    if 'name' not in kwargs:
        kwargs['name'] = args[0]

    if 'config' in kwargs:
        logging_config = kwargs['config']
    else:
        logging_config = config['Logging']

    logging_config['version'] = int( logging_config['version'] )
    logging.config.dictConfig( config['Logging'] )
    logger = logging.getLogger( 'wrair.' + kwargs['name'] )

    return logger
