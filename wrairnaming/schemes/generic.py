import re
import string
import os.path

class InvalidFormat( Exception ):
    pass

class InvalidParts( Exception ):
    pass

class OutputFormatter( object ):
    '''
        Descriptor for output formats
    '''
    def __init__( self ):
        self.format = None

    def __get__( self, instance, owner ):
        return self.format
    
    def __set__( self, instance, value ):
        '''
            Output format value should be a valid format string
            See: http://docs.python.org/2/library/string.html#string-formatting
        '''
        if not isinstance( value, str ):
            raise ValueError( "%s is not a string" % value )
        formatter = string.Formatter().parse( value )
        # Get num of fields to validate name fields later
        instance.num_output_fields = len( [f for f in formatter] )
        self.format = value

class InputFormatter( object ):
    '''
        Descriptor for input formats
    '''
    def __init__( self ):
        self.format = None

    def __get__( self, inst, itype ):
        return self.format

    def __set__( self, inst, value ):
        ''' Regular expression must be a full match as re.match will be used '''
        self.format = self._validate( value )

    def _validate( self, value ):
        if isinstance( value, str ):
            # Compile the regex
            try:
                value = re.compile( value )
            except re.error as e:
                raise ValueError( str( e ) )
        return value

class FormatScheme( object ):
    '''
        Class to ensure correct names
        given input/output formats

        Provides functionality to parse input strings and output formatted strings
    '''
    name_output_format = OutputFormatter()
    name_input_format = InputFormatter()

    def __init__( self, input_format, output_format ):
        self.name_output_format = output_format
        self.name_input_format = input_format

    def parse_input_name( self, name ):
        '''
            Parse a name using the input format
            Returns a dictionary of matched patterns
        
            Note: only parses the basename of the name
        '''
        basename = os.path.basename( name )
        m = self.name_input_format.match( basename )
        if m:
            return m.groupdict()
        raise InvalidFormat( "%s is incorrectly formatted" % name )

    def get_new_name( self, oldname ):
        parts = self.parse_input_name( oldname )
        return self.get_output_name( **parts )

    def get_output_name( self, **fileparts ):
        '''
            Returns the new name using the output_format and
            the given fileparts.
            Fileparts needs to have the same amount of keys as there are format options
        '''
        # Parse the format
        try:
            # More fileparts than output fields
            if len( fileparts ) != self.num_output_fields:
                raise KeyError()
            return self.name_output_format.format( **fileparts )
        except KeyError as e: # Gets thrown if fileparts is missing a key that the format expects
            raise InvalidParts( "Expected %d file information fields. Got %d." % (self.num_output_fields, len( fileparts )) )
