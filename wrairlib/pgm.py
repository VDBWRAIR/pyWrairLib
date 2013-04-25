### Classes to aid in demultiplexing PGM barcodes
import multiprocessing
import logging
import os

from Bio.SeqIO.SffIO import SffWriter
from Bio import SeqIO

logger = multiprocessing.get_logger()

class BarcodeConsumer( multiprocessing.Process ):
    def __init__( self, barcode_queue ):
        multiprocessing.Process.__init__( self )

        self.barcode_queue = barcode_queue

    def run( self ):
        proc_name = self.name
        logger.debug( "%s: up and running" % proc_name )
        while True:
            # Get the next barcode
            next_barcode = self.barcode_queue.get()
            # Check for poison pill
            if next_barcode is None:
                logger.debug( "%s: found poison pill" % proc_name )
                break
            # Run the barcode
            logger.info( "%s: Processing %s" % (proc_name, next_barcode.id_str) )
            next_barcode.run( proc_name )
            logger.info( "%s: Finished Processing %s" % (proc_name, next_barcode.id_str) )
        logger.debug( "%s: finishing up" % proc_name )
        return

class PGMBarcode( object ):
    """
        Represents a barcode from IonTorrent
    """
    def __init__( self, *args, **kwargs ):
        """
            args - id_str, type, sequence, floworder, index, annotation, adapter, score_mode, score_cutoff
        """
        self.id_str = kwargs['id_str']
        self.type = kwargs['type']
        self.sequence = kwargs['sequence']
        self.floworder = kwargs['floworder']
        self.index = kwargs['index']
        self.annotation = kwargs['annotation']
        self.adapter = kwargs['adapter']
        self.score_mode = kwargs['score_mode']
        self.score_cutoff = kwargs['score_cutoff']
        self.sff_file = None
        self.proc_name = None

        self.reads_sff = kwargs['sfffilepath']
        self.max_num = kwargs['max_num']
        self._processed = 0
        self._matched_reads = 0

    def _readMatches( self, read ):
        """
            read - Bio.Seq record representing a read from sff file
        """
        return self.sequence.lower() == self._getReadBarcode( read )

    def _getReadBarcode( self, read ):
        """
            Returns the barcode for a given read which should be between the flow_key and adapter sequence
        """
        start = len( read.annotations['flow_key'] )
        end = read.annotations['clip_adapter_left'] - len( self.adapter )
        seq = str( read.seq )
        return seq[start:end].lower()

    def reads_for_barcode( self, reads_file ):
        """
            Generator method returning only reads for the barcode this 
            class instance is setup for
        """
        for read in SeqIO.parse( reads_file, 'sff' ):
            # Quit if max_num is reached
            if self.max_num != 'All' and self._processed == self.max_num:
                break
            if self._readMatches( read ):
                logger.debug( "%s: %s Matched Read %s" % (self.proc_name, self.id_str, read.id) )
                self._matched_reads += 1
                yield read
            self._processed += 1

    def run( self, proc_name = None ):
        sffpath = self.id_str + '.sff'
        try:
            with open( sffpath, 'wb' ) as fh:
                self.proc_name = proc_name
                self.sff_file = SffWriter( fh )
                self.sff_file.write_file( self.reads_for_barcode( self.reads_sff ) )
                logger.info( "%s reads of %s matched %s" % (self._matched_reads, self._processed, self.id_str) )
        except ValueError:
            # No reads for barcode so remove the temporary file
            os.unlink( sffpath )
