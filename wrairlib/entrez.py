from Bio import Entrez, SeqIO
import sys
import os
import re
import time

# Defaults
Entrez.email = 'anonymous'
default_entrez_db = 'nucleotide'
default_xml = "EntrezFetch.xml"

class WEntrez:
    entrez_db = 'nucleotide'
    entrez_fetch_xml = 'EntrezFetch.xml'
    webenv = None
    querykey = None

    def __init__( self, local_xml = None ):
        if local_xml:
            self.entrez_fetch_xml = local_xml

    def _search_ncbi_sequences( self, search_term, rstart = 0, retmax = 500, increment = 500 ):
        print "Gathering id's for records for %s through %s" % (rstart,retmax)
        gids = []

        esh = Entrez.esearch( db=self.entrez_db, retstart=rstart, retmax=retmax, term=search_term )
        gis = Entrez.read( esh )
        esh.close()

        count = int( gis['Count'] )

        if rstart + retmax >= count:
            return gis['IdList']

        if rstart + (2 * retmax) >= count:
            retmax = count - (rstart + retmax)
            
        return gis['IdList'] + self._search_ncbi_sequences( search_term, rstart + increment, retmax )

    def fetch_ncbi_sequences( self, search_term ):
        """
            Fetches xml result file for a given search term from NCBI Entrez
        """

        #idlist = _search_ncbi_sequences( search_term )
        esh = Entrez.esearch( db=self.entrez_db, retmax=10000, term=search_term, usehistory='y' )
        gis = Entrez.read( esh )
        esh.close()

        idlist = gis['IdList']
        self.webenv = gis['WebEnv']
        self.querykey = gis['QueryKey']

        print "WebEnv: %s QueryKey: %s" % (self.webenv,self.querykey)
        print "Entrez Query: %s" % (search_term)
        print "Downloading %s records" % gis['Count']

        efh = Entrez.efetch( db=self.entrez_db, rettype="native", retmode="xml", usehistory='y', WebEnv=self.webenv, query_key=self.querykey )
        fh = open( self.entrez_fetch_xml, 'w+' )

        # Read a megabyte at a time for output
        count = 0
        dlstart = time.time()
        dlchunksize = 1024 * 1024
        totalbyteswritten = 0
        estrecordsize = 30000
        while True:
            chunk = efh.read( dlchunksize )
            if len( chunk ) == 0:
                break
            else:
                byteswritten = len( chunk )
                totalbyteswritten += byteswritten
            fh.write( chunk )
            count += 1
            timediff = time.time() - dlstart
            estrecords = totalbyteswritten / estrecordsize
            estspeed = totalbyteswritten / 1024 / timediff
            esttimeleft = (int( gis['Count'] ) * estrecordsize) / (estspeed / 1024)
            sys.stdout.write( "Read %s records(Estimate) at %.2f Kb/s Est. Time left: %s\r" % (estrecords, estspeed, esttimeleft) )
            sys.stdout.flush()
        print
        fh.close()
        efh.close()

    def parse_entrez( self, xml_results_file = None ):
        """
            Given an xml file name, read the file and return information about the sequences contained within
            Info gathered:
                accession
                genbank id
                title
                create year, month and day
                sequence
                locus 
        """
        if not xml_results_file:
            xml_results_file = self.entrez_fetch_xml
        # Will contain all the information keyed by genbank id
        info = {}

        fh = open( xml_results_file )
        # Potentially the file could be too large to fit into memory depending on the query.
        xml = fh.read()
        fh.close()
        
        # Pattern to pull out all Bioseq-set_seq-set pieces
        bssp = re.compile( '<Bioseq-set_seq-set>.*?</Bioseq-set_seq-set>', re.DOTALL )

        # Pattern to extract wanted info
        sep = re.compile( '<Seq-entry>.*?<Textseq-id_accession>(?P<accession>.*?)</Textseq-id_accession>.*?<Seq-id_gi>(?P<gi>.*?)</Seq-id_gi>.*?<Seqdesc_title>(?P<title>.*?)</Seqdesc_title>.*?<Date-std_year>(?P<create_year>.*?)</Date-std_year>.*?<Date-std_month>(?P<create_month>.*?)</Date-std_month>.*?<Date-std_day>(?P<create_day>.*?)</Date-std_day>.*?<IUPACna>(?P<sequence>.*?)</IUPACna>.*?<Gene-ref_locus>(?P<locus>.*?)</Gene-ref_locus>.*?</Seq-entry>', re.DOTALL )

        # Get all matches
        biosets = bssp.findall( xml )

        # The first set is not wanted as it is blank
        #del biosets[1]

        # Loop through each set and pull out the information
        for bs in biosets:
            m = sep.search( bs )
            i = m.groupdict()
            info[i['gi']] = i

        return info

    def write_fasta( self, xmlfile = None ):
        info = self.parse_entrez( xmlfile )
        fh = open( 'entrez.fna', 'w+' )

        for gi, inf in info.iteritems():
            title = inf['title']
            #title = title.split( '/' )[2]
            sequence = inf['sequence']
            fh.write( ">%s\n%s\n" % (title, sequence) )

        fh.close()

