pyWrairLib
==========

Available Scripts
-----------------

Analysis
--------
* genallcontigs.py
* genallrefstatus.sh
* genSummary.sh
 * Runs summary scripts to generate compiled summary output for GsMapper projects inside a directory
* mapSamples.py
 * Creates and runs gsmapper projects based on a RunFile
* mapSummary.py
* refstatusxls.py
* allcontig_to_allsample.py

Data
----
* splitsff
* demultiplex
* link_reads

Misc
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
