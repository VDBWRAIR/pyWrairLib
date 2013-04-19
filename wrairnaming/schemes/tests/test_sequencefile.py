import unittest
import StringIO
from configobj import ConfigObj

from sequencefile import *

class TestSequenceFile( unittest.TestCase ):
    seq_in_f = "(?P<f1>[a-z]+)__(?P<f2>[a-z])"
    seq_o_f = "{f1}/{f2}"
    fn_in_f = "(?P<f1>[a-z]+)__(?P<f2>[a-z]).fa"
    fn_o_f = "{f1}{f2}.fa"
    def test_init_param( self ):
        inst = SequenceFile( seq_in_format=self.seq_in_f, seq_out_format=self.seq_o_f,
                        file_in_format=self.fn_in_f, file_out_format=self.fn_o_f )

    def test_init_config( self ):
        s = StringIO.StringIO('''
[Test]\n
file_out_format = '%s'\n
file_in_format = '%s'\n
seq_out_format = '%s'\n
seq_in_format = '%s'\n
        ''' % (self.seq_in_f, self.seq_o_f, self.fn_in_f, self.fn_o_f))
        conf = ConfigObj( s )
        inst = SequenceFile( conf['Test'] )
