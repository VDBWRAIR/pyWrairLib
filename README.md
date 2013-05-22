pyWrairLib
==========

Available Scripts
-----------------

Analysis
--------
* genSummary.sh
 * Runs summary scripts to generate compiled summary output for GsMapper projects inside a directory
* mapSamples.py
 * Creates and runs gsmapper projects based on a RunFile
* mapSummary.py
 * Creates AllRefStatus.xls file which gives mapping depth and coverage percentage for each reference that was
   used in the reference mappings
* genallcontigs.py
 * Creates a directory containing all GsMapper project's 454AllContigs.fna+.qual consolidated into a single directory. Each AllContigs fasta+qual file is merged into a single .fastq file named after the GsMapper project directory from which it originated.
* allcontig_to_allsample.py
 * Merges a GsMapper project's 454AllContigs.fna and 454AllContigs.qual file into a single .fastq
* genallrefstatus.sh
 * Legacy shell script that merges together all found 454RefStatus.txt files into a single output stream/file
* variant_lookup
 * Script to aid in the lookup of variant information

Data
----
* splitsff
* demultiplex
* link_reads

Misc/Undocumented
----
* bestblast
* entrez_helper
* reads_for_contig
* refrename.py

Config Files
------------

MidParse.conf
-------------

This file is used by the roche software to demultiplex sff files. The contents of the file contain a mapping
between a name and a barcode sequence.
The structure of the file is as follows
```
MID
{
mid = "MIDNAME1", "BARCODESEQUENCE", MISMATCHTOLERANCE, "OPTIONAL 3' Trim Sequence";
mid = "MIDNAME2", "BARCODESEQUENCE", MISMATCHTOLERANCE, "OPTIONAL 3' Trim Sequence";
}
More information on this file can be found in the Roche documentation Part C under MIDConfig.parse
An example file that can be used is included in the config directory
```

RunFile
-------

Run files are simply a file that links a samplename to the following information about that sample
* Region number
* samplename
* virus name
 * Should conform to a valid wrair virus name(More details later on that)
* barcode/midkey name
 * Has to be a valid midkey name inside of the Midparse.conf file(for sfffile to demultiplex with using --mcf option)
* mismatch tolerance(This is really unecessary since it should be drerived from the Mid config parse file)
* reference directory/file to use to map to
 * Can be a directory of reference files or a single reference
* unique sampleid
 * Deprecated, just use the samplename
* primerfile location
 * Fasta file of primers to trim off

Listed below are [python template strings](http://docs.python.org/2/library/string.html#template-strings)
that show you the template for creating a Runfile. Basically replace anything that has a dollar sign in front of
it with a value

RunFile Header
--------------

```
# $platform sample list								
# $numregions Region $type
# Run File ID: $date.$id
!Region	Sample_name	Genotype	MIDKey_name	Mismatch_tolerance	Reference_genome_location	Unique_sample_id	Primers	
```
$platform would be replaced by Roche454 or IonTorrent
$date needs to be a valid date string that is in one of the following formats
 - DDMMYYYY
 - DD_MM_YYYY
 - YYYY_MM_DD
$id is anything that does not contain a space character

RunFile Sample Line
-------------------

```
$region	$sample	$virus	$midkey	$mismatch	$reference	$sample	$primer
```

Sample File
-----------

```
# IonExpress sample list								
# 1 Region PTP								
# Run File ID: 04192013.PGM.CPTLin
!Region	Sample_name	Genotype	MIDKey_name	Mismatch_tolerance	Reference_genome_location	Unique_sample_id	Primers	
1	D1_FST2432	Den1	IX001	0	Analysis/PipelineRuns/2013_04_19/Ref/Den1	D1_FST2432	NGSData/RawData/IonTorrent/2013_04_19/meta/Primer/Den1.fna
1	D1_FST2410	Den1	IX002	0	Analysis/PipelineRuns/2013_04_19/Ref/Den1	D1_FST2410	NGSData/RawData/IonTorrent/2013_04_19/meta/Primer/Den1.fna
```

wrairdata
=========

wrairlib
========

wrairnaming
===========

wrairanalysis
=============

mapSamples.py
-------------

mapSamples.py is used to map samples to a reference genome using the Roche Newbler mapper.
It derives all of its parameters from a RunFile.
It will create GsMapper project directories inside of the directory that you execute it from. It is usually best to create a directory to run 
this command from within.

Usage
-----

```
mapSamples.py --runfile <path to runfile>
```

genSummary.sh
-------------

This is a wrapper shell script that runs post mapping summary scripts. It doesn't generate any output or output files itself, but runs scripts that
do generate output.
It runs all scripts on all GsMapper directories found in the current directory it is executed from.
It is easy to run after mapSamples.py is run since mapSamples.py creates GsMapper projects in a directory and then you can just run genSummary.sh 
after that to get a more compiled look at all of the projects status

Currently runs:
* Gap analysis
* genallcontigs.py
* mapSummary.py 
* SequenceExtraction's Summary -table

Usage
-----

```
genSummary.sh
```

mapSummary.py
-------------

Given a directory containing gsMapper projects, this script will find all 454RefStatus.txt files and 
compiles a single Excel spreadsheet from them for all references used across all projects.
You can also specify a reference file to 'target' so that only the references inside that file will be 
listed in the output excel file.

Usage
-----

```
mapSummary.py -d <projectdir> [-r <reference>] [-o <outputfile>]
```

* projectdir can by any directory that directly contains GsMapper projects. Usually this directory is the same directory that mapSamples.py was executed from.
* reference is optional and should be one of the reference files that was used in the mapping. This basically filters out 
all references so that only the reference you specify will be listed in the output
* outputfile is optional and specifies where to write the resulting Excel file. The default is in the current directory with the name AllRefStatus.xls

genallcontigs.py
----------------

Searches inside a given directory for any gsMapper directories
For every gsMapper directory found, it gathers all contigs from the 454AllContigs.fna and writes them to a file named 
after the project directory inside of the given output directory.
The output is essentially a single directory containing Merged 454AllContigs.fna & .qual files into a .fastq file for 
each gsMapper directory

Usage
-----

```
genallcontigs.py -d <projectdir> [-o <outputdir>]
```

* projectdir can by any directory that directly contains GsMapper projects. Usually this directory is the same directory that mapSamples.py was executed from.
* outputdir is optional and defines what directory to place the results in. By default it is FastaContigs inside the current directory.

allcontig_to_allsample.py
-------------------------

Given a single gsMapper project directory, merges the 454AllContigs.fna and 454AllContigs.qual 
files into a single .fastq file Output is by default sent to STDOUT(screen) but can be set to a file by using the -o option

Usage
-----

```
allcontig_to_allsample.py -p <gsproject> [-o <outputfile>]
```

* gsproject is the path to a single Gs Project
* outputfile is optional and should be a file to write the resulting fastq to. By default it is written to the terminal

variant_lookup
-------------------------

Variant lookup looks up a position in a GsMapper alignment and displays the information about that variant
You just have to provide the nucleotide position and optionally a unique portion of the reference you are looking for.

If you do not provide the reference it will display all references for that alignment

Usage
-----

```
usage: variant_lookup [-h] [-d PDPATH] variant_pos [ref_name]

positional arguments:
  variant_pos           The variant position to display info for
  ref_name              The identifier to limit the info for. Default is to
                        show all identifiers

optional arguments:
  -h, --help            show this help message and exit
  -d PDPATH, --project_directory PDPATH
                        GsProject directory path[Default:Current working directory]
```

* variant_pos is the Nucleotide position of the alignment to look for the information for
* ref_name only has to be a portion of the reference you are looking for. This is simply a filter
  for all reference names in the alignment.
  Example:
    If the alignment has 3 references
     Reference_ABCD
     Reference_ACDE
     Reference_1

   Specifying Reference as the ref_name argument would yield all 3 references
   Specifying ABCD would only yield Reference_ABCD
   Specifying Reference_A woudl yield Reference_ABCD and Reference_ACDE
* project_directory is only used if your current working directory is not a GsMapper project. It is easiest to invoke variant_lookup
  by first changing directory to the GsMapper project you are wanting to work on.


sanger_to_fastq
---------------

Convert .ab1 files into various formats(by default fastq)
!!!Untested Script!!!
This script is under development and should be considered as such
That being said, it seems to work fine giving it the -d and -t options together


Usage
-----

```
usage: sanger_to_fastq [-h] [-s SANGERFILE] [-d SANGERDIR] [-o OUTPUTFILE]
                       [-t OUTPUTTYPE]

Convert sanger .ab1 file to another type

optional arguments:
  -h, --help            show this help message and exit
  -s SANGERFILE, --sanger-file SANGERFILE
                        Sanger file to convert
  -d SANGERDIR, --sanger-dir SANGERDIR
                        Directory containing sanger files
  -o OUTPUTFILE, --output-file OUTPUTFILE
                        The output filename. Omit an extension if you use the
                        -t fasta+qual option.
  -t OUTPUTTYPE, --output-type OUTPUTTYPE
                        The output file type. Check out
                        http://biopython.org/wiki/SeqIO for options. Use
                        fasta+qual to get both fasta and qual files
```
