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

RunFile Header
--------------

```
# $platform sample list								
# $numregions Region $type
# Run File ID: $date.$id
!Region	Sample_name	Genotype	MIDKey_name	Mismatch_tolerance	Reference_genome_location	Unique_sample_id	Primers	
```

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
