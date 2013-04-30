from schemes.generic import GenericNameFormatter
from configobj import ConfigObj

import os.path

import sys

class Formatter( object ):
    '''
        Simple wrapper around format.cfg ConfigObj
        Returns a GenericNameFormatter for any valid section

        If config is None then the default path + '/config/formats.cfg' will be used
    '''
    DEFAULT_CONF = ['config','settings.cfg']

    def __init__( self, config=None ):
        if config is None:
            # I'm so confused about python package data files and the correct
            #  way to handle them. So doing this
            config = os.path.join( sys.prefix, *self.DEFAULT_CONF)
            config = ConfigObj( config, interpolation='Template' )
        # Make sure config is a valid configobj
        if not isinstance( config, ConfigObj ):
            config = ConfigObj( config, interpolation='Template' )
        self.config = config

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
