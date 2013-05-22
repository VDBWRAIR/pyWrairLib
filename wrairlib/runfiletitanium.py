import re
from datetime import date, datetime
from wrairnaming import Formatter

from StringIO import StringIO

class RunFile( object ):
    def __init__( self, handle ):
        """
            Set the handle to the RunFile
        """
        if isinstance( handle, str ):
            handle = open( handle )
        self.handle = handle
        self.regions = []
        self.id = ""
        self._samples = []
        self.samples_by_region = {}
        self.headers = []
        self._parse()

    @property
    def samples( self ):
        '''
            Return a list of all items joined together from the regions dictionary
        '''
        return [sample for r, samples in self.samples_by_region.items() for mid, sample in samples.items()]

    def __getitem__( self, key ):
        ''' Should return list of samples for a given region '''
        return self.samples_by_region[key]

    def add_sample( self, rfsample ):
        if rfsample.region not in self.samples_by_region:
            self.samples_by_region[rfsample.region] = {}
        self.samples_by_region[rfsample.region][rfsample.midkeyname] = rfsample

    def _parse( self ):
        """
            Parse the file into the important pieces
        """
        count = 0
        for row in self.handle:
            #row = row.rstrip()
            # Get the headers
            if row.startswith( '!' ):
                self.headers = row[1:].split( '\t' )
            elif count == 0:
                self.platform = row[2:].split()[0]
                count += 1
                continue
            elif count == 1:
                self.regions, self.type = self._parse_regions_line( row )
            elif count == 2:
                stuff = self._parse_id_line( row )
                self.id = stuff['id']
                self.date = stuff['date']
            elif row.startswith( '#' ):
                count += 1
                continue
            else:
                self.add_sample( RunFileSample( row.strip(), self.date ) )
            count += 1
        # Empty runfile
        # Hack for testing: allows StringIO to be empty
        if count == 0 and not isinstance( self.handle, StringIO ):
            raise ValueError( "Empty Runfile" )

    def _parse_id_line( self, line ):
        """
            Parse Run File Id line # Run File ID: \S+

        """
        # Date formats used to parse id line
        supported_date_formats = ('%d%m%Y','%Y_%m_%d','%d_%m_%Y')
        pat = "# Run File ID: (\d{8}|\d+_\d+_\d+)\.(\S+)"
        m = re.match( pat, line )
        if not m:
            raise ValueError( "Run File ID line did not match pattern: {}".format( pat ) )
        pieces = m.groups()
        info = {}
        
        # Will be a parsed date or None indicating no match could be made
        dt = None
        for dformat in supported_date_formats:
            try:
                dt = datetime.strptime( pieces[0], dformat )
                break
            except ValueError:
                continue

        if dt is None:
            raise ValueError( "{} is an invalid date string. Supported formats are {}".format(pieces[0], supported_date_formats) )
        info['date'] = date( dt.year, dt.month, dt.day )
        info['id'] = pieces[1]
        return info

    def _parse_regions_line( self, line ):
        """
            Parse Region line # [0-9] \w+ \w+
        """
        m = re.match( '# (\d+) Region (.*)$', line )
        if not m:
            raise ValueError( "Unparsable region line: '%s'" % line )
        m = m.groups()

        # Create a tuple of regions
        regions = int( m[0] )
        if regions == 0:
            raise ValueError( "0 is not a valid amount of regions" )
        regions = tuple( range( 1, regions + 1) )

        # The Region Type
        rftype = m[1]

        return regions, rftype

class RunFileSample(object):
    SAMPLE_TEMPLATE = '{region}	{name}	{genotype}	{midkeyname}	{mismatchtolerance}	{refgenomelocation}	{uniquesampleid}	{primers}'
    NULL_REFERENCE_STR = 'User_defined_Reference'
    NULL_PRIMER_STR = 'User_defined_primers'
    REQUIRED_KWARGS = ('region','name','genotype','midkeyname','mismatchtolerance')
    OPTIONAL_KWARGS = (
        ('refgenomelocation',NULL_REFERENCE_STR),
        ('uniquesampleid',lambda x: getattr(x,'name')),
        ('primers',NULL_PRIMER_STR),
        ('disabled',False),
    )
    def __init__( self, *args, **kwargs ):
        if len( kwargs ) == 0:
            self.runfilerow = args[0]
            self.disabled = False
            self._parse_sample_row( self.runfilerow )
            if not isinstance( args[1], date ):
                raise ValueError( "{} is not a valid date object".format(args[1]) )
            self.date = args[1]
        else:
            self._setup_kwargs( kwargs )

    @property
    def refgenomelocation( self ):
        return self.__dict__['refgenomelocation']
    @refgenomelocation.setter
    def refgenomelocation( self, value ):
        nullvalues = ('-','','VOID',None,self.NULL_REFERENCE_STR)
        if value in nullvalues:
            self.__dict__['refgenomelocation'] = None
        else:
            self.__dict__['refgenomelocation'] = value

    @property
    def date( self ):
        return self.__dict__['date']
    @date.setter
    def date( self, value ):
        if not isinstance( value, date ):
            raise ValueError( "{} is not a valid date object".format(value) )
        else:
            self.__dict__['date'] = value

    @property
    def primers( self ):
        return self.__dict__['primers']
    @primers.setter
    def primers( self, value ):
        nullvalues = ('-','','VOID',None,self.NULL_PRIMER_STR)
        if value in nullvalues:
            self.__dict__['primers'] = None
        else:
            self.__dict__['primers'] = value

    def _setup_kwargs( self, kwargs ):
        ''' Handle kwargs '''
        for kwarg in self.REQUIRED_KWARGS:
            if kwarg not in kwargs:
                raise ValueError( "Missing kwarg {}".format(kwarg) )
        for kwarg, value in kwargs.items():
            setattr( self, kwarg, value )
        for oarg, default in self.OPTIONAL_KWARGS:
            if oarg not in kwargs:
                if callable( default ):
                    default = default(self)
                setattr( self, oarg, default )

    def __setattr__( self, attr, value ):
        ''' Just ensure attributes that are strings are stripped '''
        if isinstance( value, str ):
            value = value.strip()
        # Call object's setattr otherwise descriptors won't be utilized
        object.__setattr__( self, attr, value )

    def _parse_row( self, row ):
        if row.startswith( '!' ):
            raise ValueError( "Got header row from RunFile" )

    def _parse_sample_row( self, row ):
        r"""
            Parse the given row and set
            instance properties
        """
        # Should be tab delimeted
        s = row.split( '\t' )

        if len( s ) != 8:
            if len( s ) == 9 and s[8] == '':
                # Extra tab at tend of line so just ignore it
                s = s[:8]
            else:
                raise ValueError( "Sample Row does not contain all necessary columns: %s" % s )

        # Check for comment character
        if s[0].startswith( '#' ):
            self.disabled = True
            self.region = int( s[0][1:] )
        else:
            self.region = int( s[0] )
        self.name = s[1]
        self.genotype = s[2]
        self.midkeyname = s[3]
        if s[4] == '':
            self.mismatchtolerance = 0
        else:
            try:
                self.mismatchtolerance = int( s[4] )
            except ValueError as e:
                raise ValueError( "Invalid mismatch tolerance given: %s" % s[4] )
        self.refgenomelocation = s[5]
        self.uniquesampleid = s[6]
        self.primers = s[7]

    def __str__( self ):
        rstr = self.SAMPLE_TEMPLATE.format( **self.__dict__ )
        rstr = rstr.replace( 'None', self.NULL_REFERENCE_STR, 1 )
        rstr = rstr.replace( 'None', self.NULL_PRIMER_STR, 1 )
        if self.disabled:
            rstr = '#' + rstr
        return rstr

    def __unicode__( self ):
        return self.__str__()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
