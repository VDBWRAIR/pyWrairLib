import os
import os.path
import sys

from xlwt import *

def start_workbook( ):
    return Workbook()

def color_style( color ):
    return easyxf( 'font: italic on; pattern: pattern solid, fore-colour %s' % color )

def value_ok( ):
    return color_style( 'green' )

def value_caution( ):
    return color_style( 'orange' )

def value_critical( ):
    return color_style( 'red' )

class RefStatusXLS:
    BOLD_CENTER = easyxf( 'font: bold on; align: horiz center; pattern: pattern solid, fore-color grey25;' )
    BOLD = easyxf( 'font: bold on; pattern: pattern solid, fore-color grey25;' )
    CENTER = easyxf( 'align: horiz center' )
    ITALIC_WRAP = easyxf( 'font: italic on; align: horiz center, wrap on;' )
    
    def __init__( self, sheet ):
        self.sheet = sheet
        # Start in top left(After first call to set_new_project)
        self._x = -1
        self._y = 0

    @property
    def x( self ):
        srl = len( self.sorted_refs )
        if self._x == srl:
            self._x = 0
        else:
            self._x += 1
        return self._x

    @property
    def y( self ):
        return self._y

    @y.setter
    def y( self, value ):
        self._y = value

    def set_new_project( self, project ):
        '''
            Sets a new project as the base for the next data writes
        '''
        # Have to manually reset x to 0 since sorted_ref length will change
        self._x = -1 
        pd = project
        self.proj_name = os.path.split( pd.basepath.rstrip( '/' ) )[1]
        self.refstat = pd.RefStatus
        self.refstat.parse()
        self.stats = self.refstat.ref_status
        self.sorted_refs = sorted( pd.MappingProject.get_reference_names() )
        self.sorted_labels = sorted( self.stats[self.stats.keys()[0]].keys() )

    def filter_refs( self, keep_list ):
        return [ref for ref in self.sorted_refs if ref in keep_list]

    def make_sheet( self, include_only = [] ):
        '''
            Write ref status info into sheet
            Can specify a reference to include only in the output
        '''
        if isinstance( include_only, str ):
            include_only = [include_only]

        # Filter out so only include_only refs are used
        if include_only:
            self.sorted_refs = self.filter_refs( include_only )
            
        self._put_title()
        self._put_headers()
        self._put_data()

    def _put_next_cell( self, value, style = None ):
        if style is None:
            style = self.ITALIC_WRAP
        # Place the data
        x = self.x
        y = self.y
        self.sheet.write( y, x, value, style )

    def _put_title( self ):
        ''' Write the title in the top left of this sheet '''
        self._put_next_cell( self.proj_name, self.BOLD_CENTER )

    def _put_headers( self ):
        ''' Write the refrence names at top of worksheet '''
        # Each reference will now be the headers
        for header in self.sorted_refs:
            self._put_next_cell( header, self.BOLD_CENTER )
        self.y += 1

    def _put_data( self ):
        ''' Write the data into the cells '''
        blank_labels = {l:'0' for l in self.sorted_labels}
        # Loop through each label in order
        for label in self.sorted_labels:
            self._put_next_cell( label, self.BOLD )
            # Loop through each reference in order
            for ref in self.sorted_refs:
                value = self.stats.get( ref, blank_labels)[label]
                self._put_next_cell( value )
            self.y += 1
