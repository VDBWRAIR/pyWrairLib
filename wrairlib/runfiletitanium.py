import re
from datetime import date, datetime
from wrairnaming import Formatter

import settings

from StringIO import StringIO

class RunFile( object ):
    HEADER_TEMPLATE = '''# {platform} sample list
# {numregions} Region {rtype}
# Run File ID: {date:%Y_%m_%d}.{id}
!Region	Sample_name	Genotype	MIDKey_name	Mismatch_tolerance	Reference_genome_location	Unique_sample_id	Primers
'''
    REQUIRED_KWARGS = ('platform','date','samples')
    OPTIONAL_KWARGS = (('rtype','PTP'),('id','Description'),('regions',lambda x: tuple([s.region for s in x.samples])))
    supported_date_formats = ('%d%m%Y','%Y_%m_%d','%d_%m_%Y')
    def __init__( self, *args, **kwargs ):
        """
            Init a new RunFile instance given a file path or handle
            -- or --
            Init a new RunFile instance using required kwargs
                Required:
                - platform - Valid platform listed under Platforms in config file
                - date - Date of the run this runfile is for
                - samples - List of RunFileSamples
                Optional:
                - rtype - Run type. Not sure what this is exactly. Will use PTP as efault
                - id - Description with no spaces in it. Will use 'Description' as default
                - regions - Either a number of regions or a sequence of region numbers. Will gather from sample list
        """
        # Set up inst vars
        self.regions = (1,)
        self.id = ""
        self.samples_by_region = {}
        self.headers = []
        self.rtype = ''
        #self.platform = ''

        # Parse input file/path
        if len( kwargs ) == 0 and len( args ) >= 1:
            if len( args ) == 2:
                autoparse = bool(args[1])
            else:
                autoparse = True
            handle = args[0]
            if isinstance( handle, str ):
                handle = open( handle )
            self.handle = handle
            if autoparse:
                self.parse()
        else:
            self._set_kwargs( kwargs )

    @property
    def regions( self ):
        return self.__dict__.get( 'regions', () )
    @regions.setter
    def regions( self, value ):
        if type( value ) in (int,str):
            try:
                value = int( value )
                # Make sure value is not 0
                if value == 0:
                    raise ValueError( "0 is not a valid amount of regions" )
                value = tuple( range( 1, value + 1) )
            except ValueError:
                # Will get thrown below
                value = None
        elif isinstance( value, list ):
            value = tuple( value )

        if isinstance( value, tuple ) and len( value ) > 0:
            regions = tuple( [int(v) for v in value] )
            self.__dict__['regions'] = regions
            self.numregions = len( regions )
        else:
            raise ValueError( "{} is not a valid amount of regions. Regions should be an int or sequence of ints".format(value) )

    def _set_kwargs( self, kwargs ):
        for kwa in self.REQUIRED_KWARGS:
            if kwa == 'samples':
                if len( kwargs['samples'] ) == 0:
                    raise ValueError( "Need to supply list of samples instead of {}".format(kwargs['samples']) )
                [self.add_sample( s ) for s in kwargs['samples']]
                continue
            if kwa == 'date':
                self.date = self._parse_date( kwargs[kwa] )
                continue
            try:
                setattr( self, kwa, kwargs[kwa] )
            except KeyError:
                raise ValueError( "Missing kwarg {}".format( kwa ) )

        for kwa, default in self.OPTIONAL_KWARGS:
            if kwa in kwargs:
                setattr( self, kwa, kwargs[kwa] )
            else:
                if callable( default ):
                    default = default(self)
                setattr( self, kwa, default )

    def validate( self ):
        ''' Just ensure all args were setattr'd not null '''
        for kwa in self.REQUIRED_KWARGS + self.OPTIONAL_KWARGS:
            if isinstance( kwa, tuple ):
                kwa = kwa[0]
            if not getattr( self, kwa ):
                raise ValueError( "{} has not been set".format( kwa ) )

    def format_header( self ):
        ''' Return the header portion subsituting in instance variable values '''
        self.validate()
        return self.HEADER_TEMPLATE.format( **self.__dict__ )

    def __str__( self ):
        ''' Return a string representing this runfile instance that could be written to a file '''
        hdr = self.format_header()
        return hdr + "\n".join( [s.__str__() for s in self.samples] )

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

    @property
    def platform( self ):
        return self.__dict__.get( 'platform', None )

    @platform.setter
    def platform( self, value ):
        ''' Ensure valid platform '''
        value = value.strip()
        valid = False
        for plat in settings.config['Platforms'].keys():
            if value.lower() == plat.lower():
                self.__dict__['platform'] = plat
                valid = True
                break
        if not valid:
            print settings.config['Platforms'].keys()
            raise ValueError( "{} is not a supported platform in settings file".format(value) )

    def parse( self ):
        """
            Parse the file into the important pieces
        """
        count = 0
        for row in self.handle:
            # Don't do this because it could strip a needed \t off the end
            #row = row.rstrip()
            # Get the headers
            if row.startswith( '!' ):
                self.headers = row[1:].split( '\t' )
            elif count == 0:
                self.platform = row[2:].split()[0]
                count += 1
                continue
            elif count == 1:
                self.regions, self.rtype = self._parse_regions_line( row )
            elif count == 2:
                stuff = self._parse_id_line( row )
                self.id = stuff['id']
                self.date = stuff['date']
            elif row.startswith( '#' ):
                count += 1
                continue
            else:
                row = row.strip()
                # Skip empty rows
                if not row:
                    continue
                self.add_sample( RunFileSample( row, self.date ) )
            count += 1
        # Empty runfile
        # Hack for testing: allows StringIO to be empty
        if count == 0 and not isinstance( self.handle, StringIO ):
            raise ValueError( "Empty Runfile" )

    def _parse_date( self, dtstr ):
        # Will be a parsed date or None indicating no match could be made
        dt = None
        for dformat in self.supported_date_formats:
            try:
                dt = datetime.strptime( dtstr, dformat )
                break
            except ValueError:
                continue

        if dt is None:
            raise ValueError( "{} is an invalid date string. Supported formats are {}".format(dtstr, self.supported_date_formats) )

        return date( dt.year, dt.month, dt.day )

    def _parse_id_line( self, line ):
        """
            Parse Run File Id line # Run File ID: \S+

        """
        # Date formats used to parse id line
        pat = "# Run File ID: (\d{8}|\d+_\d+_\d+)\.(\S+)"
        m = re.match( pat, line )
        if not m:
            raise ValueError( "Run File ID line({}) did not match pattern: {}".format( line, pat ) )
        pieces = m.groups()
        info = {}
        
        info['date'] = self._parse_date( pieces[0] )

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
                raise ValueError( "Sample Row does not contain all necessary columns. Row given: %s" % s )

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
