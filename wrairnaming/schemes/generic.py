import re
import string
import os.path

from configobj import ConfigObj, Section

class InvalidFormat( Exception ):
    pass

class InvalidParts( Exception ):
    pass

class OutputFormatter( object ):
    '''
        Descriptor for output formats
    '''
    def __get__( self, instance, owner ):
        return getattr( instance, 'output_format', None )
    
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
        instance.output_format = value

class InputFormatter( object ):
    '''
        Descriptor for input formats
    '''
    def __get__( self, inst, itype ):
        return getattr( inst, 'input_format', None )

    def __set__( self, inst, value ):
        ''' Regular expression must be a full match as re.match will be used '''
        inst.input_format = self._validate( value )

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
        raise InvalidFormat( "%s is incorrectly formatted. Does not match pattern %s" % (name,self.name_input_format.pattern) )

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
            raise InvalidParts( "Expected %d file information fields for %s. Got %d." % (self.num_output_fields, self.output_format, len( fileparts )) )

    def __repr__( self ):
        return "FormatScheme( '{}', '{}' )".format( self.name_input_format.pattern, self.name_output_format )

class GenericNameFormatter( object ):
    '''
        Abstract class to allow easy ConfigObj attr_in/out_format Sections to be initialized
    '''
    def __init__( self, *args, **kwargs ):
        '''
            Accepts a ConfigObj.Section(or dictionary i guess will work too) or any amount of kwargs
                kwargs or section keys are to be in pairs of formatters
                <name>_in_format & <name>_out_format and be valid parameters for
                InputFormatter and OutputFormatter
        '''
        # Detect ConfigObj.Section
        if len( args ) == 1 and isinstance( args[0], Section ):
            formats = args[0]
        else:
            # or just use kwargs for source
            formats = ConfigObj( kwargs )

        if len( formats ) < 2:
            raise ValueError( "Incorrect amount of formats provided" )

        # Detect formatters and set instance attributes/methods
        self._setup_inst( formats )

    def _setup_inst( self, formats ):
        '''
            Setup FormatScheme instance attributes using simple split on keys of formats
            First item is the name, second item is in/out
        '''
        attrs = self._get_format_attrs( formats )
        # Set instance attributes
        for k,v in attrs.items():
            if not ('in' in v or 'out' in v):
                raise ValueError( "%s does not have in and out format" % k )
            else:
                self._set_format_attr( k, v )
                self._set_format_attrmethod( k )

    def _get_format_attrs( self, formats ):
        '''
            Get attributes dictionary from formats parameter dictionary
        '''
        attributes = {}
        # Compile a list of attributes
        for k,v in formats.items():
            # Ignores non format keys
            if '_in_' in k or '_out_' in k:
                # The names need to be name_in|out_whatever
                try:
                    name, inout, _ = k.split( '_' )
                except ValueError as e:
                    raise ValueError( "Incorrect attribute format given {}. Valid attributes should be <name>_in|out_format.".format(k) )
                if not name:
                    raise ValueError( "Attribute format {} does not contain a name at the beginning".format(k) )
                attrname = "%s_format" % name
                if attrname not in attributes:
                    attributes[attrname] = {}
                attributes[attrname][inout] = v
        if len( attributes ) > 0:
            return attributes
        else:
            raise ValueError( "Incorrect amount of formats provided" )

    def _set_format_attr( self, attrname, formats ):
        '''
            Create instance attributes from attributes
        '''
        fs = FormatScheme( formats['in'], formats['out'] )
        setattr( self, attrname, fs )

    def _set_format_attrmethod( self, attrname ):
        '''
            Essentially alias the FormatScheme's get_new_name to self.rename_attrname
        '''
        # methodname with _format stripped off
        methname = "rename_%s" % attrname.rstrip( '_format' )
        # The function to alias
        func = getattr( self, attrname ).get_new_name
        # Alias self.<methname> to func
        setattr( self, methname, func )
