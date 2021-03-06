import os
import os.path
import glob

import nose

import common
import fixtures

from .. import demultiplex

from wrairlib.runfiletitanium import RunFile

def avail_cmds( ):
    ''' Get available cmds that can be run from os.environ['PATH'] '''
    cmds = {}
    for pdir in os.environ['PATH'].split(':'):
        try:
            for cmd in glob.glob( os.path.join( os.path.abspath( pdir ), '*' ) ):
                cmds[os.path.basename(cmd)] = cmd 
        except OSError as e:
            continue
    return cmds
''' Cache the avail_cmds '''
_avail_cmds = avail_cmds()

def which( cmd ):
    ''' Implement UNIX which '''
    return _avail_cmds[cmd]

def read_list_results( ):
    ''' Return read lists indexed by sff file '''
    ret = {}
    for name, path in fixtures.demultiplex_reads_lst().items():
        n,e = os.path.splitext( name )
        sffn = "{}.{}".format(n,'sff')
        ret[sffn] = demultiplex.ReadList.parse( path )
    return ret

class TestSortMidlist( object ):
    def test_doesitwork( self ):
        lst = ['a1', 'a10', 'a01']
        expect = ['a1', 'a01', 'a10']
        result = demultiplex.sort_midlist( lst )
        common.ere( expect, result )

class TestDemultiplexSff( common.BaseClass ):
    sffs = fixtures.multiplex_sffs()
    rf = RunFile( fixtures.RUNFILE_PATH )
    expected_read_list = fixtures.demultiplex_reads_lst( )
    sfffilecmd = which( 'sfffile' )
    def setUp( self ):
        super( TestDemultiplexSff, self ).setUp()

    def test_ensureabspath( self ):
        ''' sfffile, midparsefile, sfffilecmd and outputdir all need to abspaths '''
        try:
            demultiplex.demultiplex_sff( 'sfffile', 'MidParse.conf', ['Mid1'], 'sfffilecmd', 'outputdir' )
            assert False, 'Should have raised exception as there is a non abspath'
        except ValueError as e:
            assert True

    def test_outputdir_notexist( self ):
        ''' Make sure outputdir gets created if it doesn't exist '''
        sffn, sffp = self.sffs.items()[0]
        try:
            demultiplex.demultiplex_sff( sffp, fixtures.MIDPARSE, ['Mid1'], self.sfffilecmd, 'outputdir' )
            assert True
        except OSError as e:
            assert False, 'Output dir didn\'t exist and threw an error which is incorrect'

    def test_emptymidlist( self ):
        ''' Empty midlist should raise exception '''
        try:
            demultiplex.demultiplex_sff( '', '', [], '', '' )
            assert False, 'Empty midlist did not raise exception'
        except ValueError as e:
            assert True

    def test_midlist_missing( self ):
        sffn, sffp = self.sffs.items()[0]
        reg = int( sffn.replace( '.sff', '' )[-2:] )
        process = demultiplex.demultiplex_sff( sffp, fixtures.MIDPARSE, self.rf[reg].keys() + ['RL99'], self.sfffilecmd, self.tempdir )
        stdout, stderr = process.communicate()
        read_lst = self.expected_read_list[sffn.replace( '.sff', '.lst' )]
        with open( read_lst ) as fh:
            result = fh.read() + '  '+fixtures.MIDPREFIX+'RL99:  0 reads found\n'
            common.erdiff( result, stdout )

    def test_midlist_missingrev( self ):
        ''' Make sure only midkey list barcodes are extracted '''
        sffn, sffp = self.sffs.items()[0]
        reg = int( sffn.replace( '.sff', '' )[-2:] )
        keys = demultiplex.sort_midlist( self.rf[reg].keys() )[:-2]
        process = demultiplex.demultiplex_sff( sffp, fixtures.MIDPARSE, keys, self.sfffilecmd, self.tempdir )
        stdout, stderr = process.communicate()
        read_lst = self.expected_read_list[sffn.replace( '.sff', '.lst' )]
        with open( read_lst ) as fh:
            expect = "".join(fh.readlines()[:-2])
            common.erdiff( expect, stdout )

    def test_demultiplex_sff( self ):
        ''' Should match expected output from fixtures '''
        for sffn, sffp in self.sffs.items():
            reg = int( sffn.replace( '.sff', '' )[-2:] )
            read_lst = self.expected_read_list[sffn.replace( '.sff', '.lst' )]
            process = demultiplex.demultiplex_sff( sffp, fixtures.MIDPARSE, self.rf[reg].keys(), self.sfffilecmd, self.tempdir )
            stdout, stderr = process.communicate()
            with open( read_lst ) as fh:
                common.erdiff( fh.read(), stdout )

class TestDemultiplex( common.BaseClass ):
    rf = RunFile( fixtures.RUNFILE_PATH )
    mp = fixtures.MIDPARSE 
    sffc = which( 'sfffile' )
    fp = fixtures.FIXTURE_PATH
    rdl = read_list_results()
    def test_ensureoutputdir( self ):
        ''' Make sure output dir is created if it doesn't exist '''
        outdir = os.path.join( self.tempdir, 'test' )
        results = demultiplex.demultiplex( self.fp, outdir, self.rf, self.mp, self.sffc )
        common.ere( True, os.path.isdir( outdir ) )
        common.ere( self.rdl, results )

    def test_outputdiraleady( self ):
        ''' Output directory already created '''
        outdir = self.tempdir
        results = demultiplex.demultiplex( self.fp, outdir, self.rf, self.mp, self.sffc )
        # Get region list
        expected_dirs = [str(int(os.path.splitext(n)[0][-2:])) for n in fixtures.multiplex_sffs()]
        # Ensure output directory created
        common.ere( True, os.path.isdir( outdir ) )
        # Ensure region directories
        common.ere( expected_dirs, os.listdir( outdir ) )
        # Ensure results are correct
        common.ere( self.rdl, results )

    def test_runfiletype( self ):
        ''' Make sure that an opened file for a runfile is handled '''
        with open( fixtures.RUNFILE_PATH ) as fh:
            try:
                demultiplex.demultiplex( self.fp, self.tempdir, fh, self.mp, self.sffc )
                assert True
            except Exception as e:
                print e
                assert False, "RunFile opened file given to demultiplex raised an error"

    def test_runfilenone( self ):
        ''' RunFile is None '''
        try:
            demultiplex.demultiplex( self.fp, self.tempdir, None, self.mp, self.sffc )
            assert False
        except ValueError as e:
            assert True

    def test_sffdirnotexists( self ):
        ''' sff dir does not exist '''
        try:
            results = demultiplex.demultiplex( '/missing/path', self.tempdir, self.rf, self.mp, self.sffc )
            assert False, "demultiplex did not raise ValueError with invalid path"
        except ValueError as e:
            assert True

    def test_singleinputsff( self ):
        ''' Make sure single sff works '''
        multiplex_files = fixtures.multiplex_sffs().items()
        sfffile = multiplex_files[0][0]
        expect = os.path.join( self.tempdir, 'sff', sfffile )
        os.mkdir( 'sff' )
        # symlink in a fixture sff file
        os.symlink( multiplex_files[0][1], expect )
        outdir = os.path.join( self.tempdir, 'test' )
        results = demultiplex.demultiplex( 'sff', outdir, self.rf, self.mp, self.sffc )
        expected_dirs = [str(int(os.path.splitext(expect)[0][-2:]))]
        common.ere( expected_dirs, os.listdir( outdir ) )
        common.ere( {sfffile:self.rdl[sfffile]}, results )

    def test_blanksffnooutput( self ):
        ''' Make sure outputdir is not created if no sff files found '''
        outputdir = os.path.join( self.tempdir, 'emptydir' )
        results = demultiplex.demultiplex( self.tempdir, outputdir, self.rf, self.mp, self.sffc )
        common.ere( False, os.path.isdir( outputdir ) )

# Lazy alias
drds = demultiplex.rename_demultiplexed_sffs
class TestRenameDemultiplexedSffs( common.BaseClass ):
    def setUp( self ):
        super( TestRenameDemultiplexedSffs, self ).setUp()
        #self.mock_ddir = fixtures.mock_demultiplex_directory()

    def make_ddir( self, sffs ):
        ''' Create mock directory from dictionary '''
        for rdir, sffs in sffs.items():
            os.mkdir( rdir )
            os.chdir( rdir )
            for sff in sffs:
                common.create( sff )
            os.chdir( '../' )

    def test_empty( self ):
        ''' Make sure an empty directory works '''
        # Don't raise an exception
        drds( self.tempdir, fixtures.RUNFILE_PATH )

    def test_mixed_files( self ):
        ''' Make sure all files in root are ignored '''
        ddir = 'demultiplex_by_region'
        expect = ['454Reads.'+fixtures.MIDPREFIX+'RL1.sff','ignore.me']
        os.mkdir( ddir )
        os.chdir( ddir )
        for f in expect:
            common.create( f )
        os.chdir( self.tempdir )
        drds( ddir, fixtures.RUNFILE_PATH )
        result = os.listdir( ddir )
        # Just ensure that the files in root didn't change
        common.ere( expect, result )

    def test_single_region_empty( self ):
        ''' Make sure single empty region dir failes gracefully '''
        mock_d = {'1':[]}
        self.make_ddir(mock_d)
        # No exception wanted here
        drds( self.tempdir, fixtures.RUNFILE_PATH )

    def test_single_region_single( self ):
        ''' Make sure a single region with single file works '''
        mock_d = {'1':['454Reads.'+fixtures.MIDPREFIX+'RL1.sff']}
        self.make_ddir( mock_d )
        drds( self.tempdir, fixtures.RUNFILE_PATH )
        expect = {1:['Sample1__1__RL1__2013_05_01__pH1N1.sff']}
        result = fixtures.mock_demultiplex_directory( self.tempdir )
        common.ere( expect, result )

    def test_single_region_multi( self ):
        ''' Make sure a single region with multiple files works '''
        mp = fixtures.MIDPREFIX
        mock_d = {'1':['454Reads.'+mp+'RL1.sff','454Reads.'+mp+'RL2.sff']}
        self.make_ddir( mock_d )
        drds( self.tempdir, fixtures.RUNFILE_PATH )
        expect = {1:['Sample1__1__RL1__2013_05_01__pH1N1.sff','Sample2__1__RL2__2013_05_01__pH1N1.sff']}
        result = fixtures.mock_demultiplex_directory( self.tempdir )
        common.ere( expect[1], result[1] )

    def test_multi_region_all_empty( self ):
        ''' Make sure multiple regions that are all empty work '''
        mock_d = {'1':[],'2':[]}
        self.make_ddir( mock_d )
        drds( self.tempdir, fixtures.RUNFILE_PATH )
        result = fixtures.mock_demultiplex_directory( self.tempdir )
        expect = {1:[],2:[]}
        common.ere( expect, result )

    def test_multi_region_all_single( self ):
        ''' Make sure multiple regions that have single files work '''
        mp = fixtures.MIDPREFIX
        mock_d = {'1':['454Reads.'+mp+'RL1.sff'],'2':['454Reads.'+mp+'TI1.sff']}
        self.make_ddir( mock_d )
        drds( self.tempdir, fixtures.RUNFILE_PATH )
        result = fixtures.mock_demultiplex_directory( self.tempdir )
        expect = {1:['Sample1__1__RL1__2013_05_01__pH1N1.sff'],2:['Sample52__2__TI1__2013_05_01__Den4.sff']}
        common.ere( expect, result )

    def test_multi_region_all_multi( self ):
        ''' Make sure multiple regions that have multiple files work '''
        mp = fixtures.MIDPREFIX
        mock_d = {'1':['454Reads.'+mp+'RL1.sff','454Reads.'+mp+'RL2.sff'],'2':['454Reads.'+mp+'TI1.sff','454Reads.'+mp+'TI2.sff']}
        self.make_ddir( mock_d )
        drds( self.tempdir, fixtures.RUNFILE_PATH )
        result = fixtures.mock_demultiplex_directory( self.tempdir )
        expect = {1:['Sample1__1__RL1__2013_05_01__pH1N1.sff','Sample2__1__RL2__2013_05_01__pH1N1.sff'],2:['Sample52__2__TI1__2013_05_01__Den4.sff','Sample53__2__TI2__2013_05_01__Den4.sff']}
        common.ere( expect[1], result[1] )
        common.ere( expect[2], result[2] )

    def test_missingfromrunfile( self ):
        ''' Make sure sff files in the directory that are not in runfile are ignored '''
        mock_d = {'1':['454Reads.'+fixtures.MIDPREFIX+'RL1.sff','454Reads.'+fixtures.MIDPREFIX+'IX1.sff']}
        self.make_ddir( mock_d )
        drds( self.tempdir, fixtures.RUNFILE_PATH )
        result = fixtures.mock_demultiplex_directory( self.tempdir )
        expect = {1:['Sample1__1__RL1__2013_05_01__pH1N1.sff','454Reads.'+fixtures.MIDPREFIX+'IX1.sff']}
        common.ere( expect[1], result[1] )
