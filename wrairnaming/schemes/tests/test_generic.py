import unittest
import sys
import re

from generic import *

class TestWithDesc(object):
    outputf = OutputFormatter()
    inputf = InputFormatter()

class FormatterTest( unittest.TestCase ):
    def setUp( self ):
        self.inst = TestWithDesc()

class InputFormatterTest( FormatterTest ):
    def test_get( self ):
        self.assertEqual( self.inst.inputf, None )

    def test_set_valid( self ):
        value = '(?P<good>.*)'
        self.inst.inputf = value
        self.assertTrue( isinstance( self.inst.inputf, type( re.compile( '' ) ) ) )

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
