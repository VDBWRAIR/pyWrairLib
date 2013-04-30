import nose
from ..formatter import Formatter
from ..schemes.generic import GenericNameFormatter

from configobj import ConfigObj

class TestFormatter( object ):
    def defaultconfig( self ):
        return Formatter()

    def otherconfig( self ):
        from StringIO import StringIO
        conf = ConfigObj( StringIO( '''
[FormatSection1]
attr1_in_format = "(?P<n1>[a-z])__(?P<n2>[a-z])"
attr1_out_format = "{n1}|{n2}"
''') )
        return Formatter( conf )

    def test_defaultconfig( self ):
        assert isinstance( self.defaultconfig(), Formatter )

    def test_otherconfig( self ):
        assert isinstance( self.otherconfig(), Formatter )

    def test_getformatterfor( self ):
        finst = self.otherconfig().get_formatter_for( 'FormatSection1' )
        assert isinstance( finst, GenericNameFormatter )
        assert finst.rename_attr1( 'a__b' ) == 'a|b'

    def test_getattr( self ):
        finst = self.otherconfig().FormatSection1
        assert isinstance( finst, GenericNameFormatter )
        assert finst.rename_attr1( 'a__b' ) == 'a|b'

    def test_cacheattr( self ):
        formatter = self.otherconfig()
        assert formatter.FormatSection1 is formatter.FormatSection1
        assert formatter.get_formatter_for('FormatSection1') is formatter.get_formatter_for('FormatSection1')

    def test_badsection( self ):
        formatter = self.otherconfig()
        try:
            formatter.MissingSection
            assert False, "Did not raise AttributeError for missing section"
        except AttributeError as e:
            assert True
