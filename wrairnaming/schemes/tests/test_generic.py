import unittest
import sys
import re
import nose

from ..generic import *
from configobj import ConfigObj

class TestWithDesc(object):
    outputf = OutputFormatter()
    inputf = InputFormatter()

class FormatterTest( unittest.TestCase ):
    def setUp( self ):
        self.inst = TestWithDesc()
        self.inst2 = TestWithDesc()

class InputFormatterTest( FormatterTest ):
    def test_get( self ):
        self.assertEqual( self.inst.inputf, None )

    def test_set_valid( self ):
        value = '(?P<good>.*)'
        self.inst.inputf = value
        self.assertTrue( isinstance( self.inst.inputf, type( re.compile( '' ) ) ) )

    def test_twoinst( self ):
        self.inst.inputf = 'reg1'
        self.inst2.inputf = 'reg2'
        assert self.inst.inputf.pattern != self.inst2.inputf.pattern, 'Instances should not have same input patterns'

    def test_set_invalid( self ):
        value = '(?P<good>.*'
        self.assertRaises( ValueError, self.inst.inputf, value )

class OutputFormatterTest( FormatterTest ):
    def test_get( self ):
        self.assertEqual( self.inst.outputf, None )
    
    def test_set_valid( self ):
        value = '{good}'
        self.inst.outputf = value
        self.assertEqual( self.inst.outputf, value )

    def test_towinst( self ):
        self.inst.outputf = 'form1'
        self.inst2.outputf = 'form2'
        assert self.inst.outputf != self.inst2.outputf, 'Instances should not have same output patterns'

    def test_set_invalid( self ):
        value = '{incorrect'
        self.assertRaises( ValueError, self.inst.outputf, value )

class FormatSchemeTest( unittest.TestCase ):
    def setUp( self ):
        self.inf = "(?P<field1>[a-z])__(?P<field2>[a-z])"
        self.outf = "{field1}_{field2}"
        self.inst = FormatScheme( self.inf, self.outf )

    def test_construct_ivalid( self ):
        self.assertRaises( ValueError, FormatScheme, "(", "{}" )
        self.assertRaises( ValueError, FormatScheme, "()", "{" )

    def test_parseinputname_valid( self ):
        tests = {
            'absfn':'/some/path/a__b',
            'relfn':'some/path/a__b',
            'fn':'a__b'
        }
        for test, fn in tests.items():
            self.assertTrue( isinstance( self.inst.parse_input_name( fn ), dict ) )

    def test_parseinputname_invalid( self ):
        tests = {
            'absfn':'/some/path/a__',
            'relfn':'some/path/a__',
            'fn':'a__'
        }
        for test, fn in tests.items():
            self.assertRaises( InvalidFormat, self.inst.parse_input_name, fn )

    def test_getoutputname_valid( self ):
        test = {'field1':'a', 'field2':'b'}
        self.assertEqual( self.inst.get_output_name( **test ), 'a_b' )

    def test_getoutputname_invalid( self ):
        tests = [
            {'field1':'a'},
            {'field2':'b'},
            {},
            {'field1':'a', 'field2':'b', 'extrafield':'c'}
        ]
        for test in tests:
            self.assertRaises( InvalidParts, self.inst.get_output_name, **test )

    def test_getnewname_valid( self ):
        tests = {
            'absfn':'/some/path/a__b',
            'relfn':'some/path/a__b',
            'fn':'a__b'
        }
        for name, fn in tests.items():
            self.assertEqual( self.inst.get_new_name( fn ), 'a_b' )

    def test_getnewname_invalid( self ):
        tests = {
            'absfn':'/some/path/a__',
            'relfn':'some/path/a__',
            'fn':'a__'
        }
        for name, fn in tests.items():
            self.assertRaises( InvalidFormat, self.inst.get_new_name, fn )

class GenericNameFormatterTest( unittest.TestCase ):
    def setUp( self ):
        # Mock section these are set up to reverse each other
        self.mock_section = {
            'attr1_in_format': '(?P<name1>[a-z])__(?P<name2>[a-z])',
            'attr1_out_format': '{name1}|{name2}',
            'attr2_in_format': '(?P<name1>[a-z])\|(?P<name2>[a-z])',
            'attr2_out_format': '{name1}__{name2}'
        }
        self.inst = GenericNameFormatter( fake_in_format="",fake_out_format="" )
        self.inst2 = GenericNameFormatter( **self.mock_section )

    def test_initvalid( self ):
        # Fake a kwargs argument
        assert isinstance( GenericNameFormatter( **self.mock_section ), GenericNameFormatter )
        # Fake a Configobj argument
        assert isinstance( GenericNameFormatter( ConfigObj( self.mock_section ) ), GenericNameFormatter )

    def test_getformaattrs1( self ):
        try:
            self.inst._get_format_attrs( {} )
            assert False, 'Failed to raise ValueError for empty formats dict'
        except ValueError as e:
            assert str( e ) == 'Incorrect amount of formats provided'

    def test_getformatattrs2( self ):
        try:
            self.inst._get_format_attrs( {'bob':1, 'sally':2} )
            assert False, 'Failed to raise ValueError for invalid formatted dict keys'
        except ValueError as e:
            assert 'Incorrect format given' in str( e ), "Expected Incorrect format given in exception message " + str( e )

    def test_invalidmissingin( self ):
        del self.mock_section['attr2_in_format']
        try:
            self.inst._get_format_attrs( self.mock_section )
        except ValueError as e:
            assert 'does not have in and out format' in str( e )

    def test_invalidmissingout( self ):
        del self.mock_section['attr2_out_format']
        try:
            self.inst._get_format_attrs( self.mock_section )
        except ValueError as e:
            assert 'does not have in and out format' in str( e )

    def test_setformatattrs( self ):
        for k in sorted( self.mock_section.keys() )[::2]:
            attr = k.replace( '_in', '' )
            attr = getattr( self.inst2, attr )
            assert isinstance( attr, FormatScheme ), '%s is instance of FormatScheme' % attr
            atrinputpat = attr.name_input_format.pattern
            actualpat = self.mock_section[k]
            assert atrinputpat == actualpat, '%s should equal %s' % (atrinputpat, actualpat)

    def test_setattrmethods( self ):
        assert hasattr( self.inst2, 'rename_attr1' )
        assert hasattr( self.inst2, 'rename_attr2' )

    def test_renameworks( self ):
        orig = 'a__b'
        # newn should be a|b
        newn = self.inst2.rename_attr1( orig )
        # origname should be a__b
        origname = self.inst2.rename_attr2( newn )
        assert newn == 'a|b', 'newn = "%s" should be %s' % (newn, 'a|b')
        assert origname == orig, 'origname = "%s" should be %s. %s' % (origname,orig,self.inst2.attr2_format)

    def test_invalidinputrename( self ):
        try:
            self.inst2.rename_attr1( 'a__1' )
            assert False, 'InvalidFormat not raised'
        except InvalidFormat as e:
            assert True, 'InvalidFormat raised'

if __name__ == '__main__':
    nose.run()
