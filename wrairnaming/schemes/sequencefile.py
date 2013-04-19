import re

from generic import FormatScheme

from configobj import Section

class SequenceFile( object ):
    '''
        Abstract class to ensure correct identifeir names
    '''
    def __init__( self, *args, **kwargs ):
        '''
            Params:
                Either:
                    first argument is a ConfigObj.Section with the following options, or just the following as
                        kwargs
                    seq_in_format - Sequence Identifier Input Regular Expression
                    seq_out_format - Format String for Identifier Output
                    file_in_format - Filename input Regular Expression
                    file_out_format - Format string for File Output Format
        '''
        # If the first argument was a configobj section
        if len( args ) == 1 and isinstance( args[0], Section ):
            formats = args[0]
        else:
            # Fall back and use kwargs
            formats = kwargs

        # Make sure that the required arguments exists
        try:
            sif = formats['seq_in_format']
            sof = formats['seq_out_format']
            fif = formats['file_in_format']
            fof = formats['file_out_format']
        except KeyError as e:
            raise TypeError( str( e ) )

        self.seq_id_format = FormatScheme( sif, sof )
        self.file_format = FormatScheme( fif, fof )

    def rename_file( self, oldname ):
        return self.rename_( 'file', oldname )

    def rename_seq( self, oldname ):
        return self.rename_( 'seq', oldname )

    def rename_( self, file_or_seq, oldname ):
        if file_or_seq == 'file':
            return self.file_format.get_output_name( oldname )
        if file_or_seq == 'seq':
            return self.seq_id_format.get_output_name( oldname )
