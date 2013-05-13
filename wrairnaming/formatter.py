from schemes.generic import GenericNameFormatter
from configobj import ConfigObj
from wrairlib.settings import config

import os.path

import sys

class Formatter( object ):
    '''
        Simple wrapper around format.cfg ConfigObj
        Returns a GenericNameFormatter for any valid section
    '''
    def __init__( self, pconfig=None ):
        # Use default config
        if pconfig is None:
            self.config = config
        # Make sure config is a valid configobj
        elif not isinstance( pconfig, ConfigObj ):
            self.config = ConfigObj( pconfig, interpolation='Template' )
        else:
            self.config = pconfig

        self._formattercache = {}

    def get_formatter_for( self, sectiontitle ):
        '''
            Return GenericNameFormatter for a section title
        '''
        try:
            return getattr( self, sectiontitle )
        except AttributeError as e:
            raise ValueError( str( e ) )

    def __getattr__( self, attr ):
        '''
            Return from formatter cache or get the formatter
        '''
        if attr in self.config.sections:
            if attr not in self._formattercache:
                self._formattercache[attr] = GenericNameFormatter( self.config[attr] )
            return self._formattercache[attr]
        else:
            raise AttributeError( "%s is not a valid section title. Valid sections are %s" % (attr,self.config.sections) )
