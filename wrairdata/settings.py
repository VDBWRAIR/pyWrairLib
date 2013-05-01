import os.path
import stat
import logging
import sys

from configobj import ConfigObj

config = ConfigObj( os.path.join( sys.prefix, 'config', 'settings.cfg' ), interpolation='Template' )

# Log level DEBUG, WARNING, INFO
LOG_LEVEL = getattr( logging, config['DEFAULT']['LOG_LEVEL'] )
