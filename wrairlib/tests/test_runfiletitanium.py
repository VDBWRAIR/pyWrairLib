import nose

from StringIO import StringIO
from datetime import date
import string

from ..runfiletitanium import RunFile

# Mock an empty runfile so we can instantiate the RunFile class
#  without giving it an actual file
empty_runfile = StringIO( "" )

##########################
##### parse_id_line ######
##########################
def parseidline( line ):
    return RunFile( empty_runfile )._parse_id_line( line )

def test_pil_valid():
    line = "# Run File ID: 12232011.AFRIMS_Den2AndPathogenDiscovery"
    pieces = parseidline( line )
    assert pieces == {'date':date(2011,12,23), 'id':'AFRIMS_Den2AndPathogenDiscovery'}, pieces

def test_pil_emptyline():
    line = ""
    try:
        parseidline( line )
        assert False, "Did not raise ValueError"
    except ValueError as e:
        assert True

def test_pil_invaliddate():
    lines = [
        "# Run File ID: 111979.NonZeroPadded",
        "# Run File ID: 33011979.BadMonth",
        "# Run File ID: 01331979.BadDay", 
    ]
    for line in lines:
        try:
            parseidline( line )
            assert False, "Did not raise ValueError: " + line
        except ValueError as e:
            assert True

def test_pil_missinghash():
    line = "Run File ID: 01011979.MissingHash"
    try:
        parseidline( line )
        assert False, "Did not raise ValueError"
    except ValueError as e:
        assert True

###############################
##### parse_regions_line ######
###############################
def parseregionsline( line ):
    return RunFile( empty_runfile )._parse_regions_line( line )

def test_prl_valid():
    line = "# 2 Region PTP"
    pieces = parseregionsline( line )
    assert pieces == ((1,2), 'PTP'), pieces

def test_prl_empty():
    line = ""
    try:
        parseregionsline( line )
        assert False, 'Did not raise ValueError for empty line'
    except ValueError:
        assert True

def test_prl_missinghash():
    line = "2 Region PTP"
    try:
        parseregionsline( line )
        assert False, 'Did not raise ValueError for missing hash'
    except ValueError:
        assert True

def test_prl_typehasgoofychars():
    rtype = string.printable.replace( '\n', '' )
    line = "# 2 Region " + rtype
    pieces = parseregionsline( line )
    assert pieces == ((1,2), rtype), pieces

def test_prl_zeroregions():
    line = "# 0 Region PTP"
    try:
        parseregionsline( line )
        assert False, 'ValueError not raised for 0 regions'
    except ValueError:
        assert True

###############
#### parse ####
###############
header_template = string.Template('''# $platform sample list								
# $regions Region $rtype								
# Run File ID: $date.$id
$headerline''')
hdr = '!Region	Sample_name	Genotype	MIDKey_name	Mismatch_tolerance	Reference_genome_location	Unique_sample_id	Primers'

def test_p_valid():
    rf = StringIO( header_template.substitute( platform='platform', regions='2', rtype='PTP', date='01011979', id='testfile', headerline=hdr ) )
    print rf.getvalue()
    RunFile( rf )
