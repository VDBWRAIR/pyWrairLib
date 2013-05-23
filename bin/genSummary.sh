#!/usr/bin/env bash

##############################################################################
##  Author: Tyghe Vallard
##  Date: 3/21/2013
##  Email: vallardt@gmail.com
##  Purpose:
##      Automatically generate all post Mapping summaries for a
##      bunch of gsMapper directories
##      Any gsMapper directory with the following name scheme
##          .*__.*__.*
##      will be included in the post Mapping summaries
##      Currently the following summaries are generated:
##          - Mapping Summary table from SequenceExtraction's Summary -table
##          - FastaContigs folder from genallcontigs.py
##          - Gaps directory from running gapsformids.py(NGSCoverage)
##          - Each Flu segment's gaps split out
##          - Each Flu segment's gap graph from gapstoscatter(NGSCoverage)
##  Version:
##      1.0 -
##          Initial Script
##          Needs some refinement as it is a bit rough around the edges
##          Should accept a directory as an argument instead of forcing user
##          to run it within the top level directory of an analysis
##      1.1 -
##          Fixed a bug with the way it renamed the Segment gaps
##############################################################################

# This directory
this_dir=$(cd $(dirname $0) && pwd)

# Array of segment names(IGN is just a placeholder for 0 index)
segment_names=( IGN PB2 PB1 PA HA NP NA MP NS )

gapdir="Gaps"

# Cleanup old run if there
rm -rf "${gapdir}"

# Make sure the Gaps directory is there
mkdir "${gapdir}"

# Get gaps for all projects for this virus
find . -mindepth 1 -maxdepth 1 -type d | grep '.*__.*__.*' | sed 's/\.\///' | gapsformids.py -o "${gapdir}"

# Cat all samples that have gaps into all.gaps inside virus folder
for gapfile in ${gapdir}/*
do
    lines=$(wc -l ${gapfile} | cut -d' ' -f1)
    if [ $lines -gt 1 ]
    then
        cat ${gapfile} >> ${gapdir}/all.gaps
    fi
done

# Make sure all.gaps exists
if [ -e ${gapdir}/all.gaps ]
then
    mkdir ${gapdir}/Segments
    # Separate all segment gap files
    # Gathers all the unique segment types
    # !! Assumes reference names all end in segment name !!
    virus_names=$(awk -F'/' '/,/ {print $1}' ${gapdir}/all.gaps | sort | uniq)
    for virus in ${virus_names}
    do
        seg_names=$(grep "^${virus}" ${gapdir}/all.gaps | cut -d'/' -f5 | cut -d'|' -f1 | sort | uniq)
        for segname in ${seg_names}
        do
            # Prepends sample name to gap line and removes reference name
            egrep "(.*__.*__.*)$|^${virus}.*/${segname}\|" Gaps/all.gaps | grep -B 1 "${segname}|" | grep -v '\-\-' | xargs -n 2 | sed "s%\(.*__.*__.*\)\s.*/${segname}|%\1|%" > ${segfile}.gaps

            # Generate the Graphic
            if [ -e ${segfile}.gaps ]
            then
                gapstoscatter --csv ${segfile}.gaps -o ${segfile}.png -t "${virus} Segment ${segname}"
            fi
        done
    done
else
    echo "----------------------------------------------"
    echo "There were no gaps found for any samples/genes"
    echo "----------------------------------------------"
fi

# Generate summary table
if [ ! -e workfile ]
then
    mkdir workfile
fi

# Generate Summary Table
/home/EIDRUdata/Tyghe/Dev/SequenceExtraction/bin/Summary -seDir $(pwd) -table > workfile/summary.tsv
# Generate FastaContigs folder
${this_dir}/genallcontigs.py -d $(pwd)
# Generate All454RefStatus.tsv
${this_dir}/mapSummary.py -d $(pwd) -o workfile/All454RefStatus.xls

# Ensure permissions are good to go
chown -R :eidru $(pwd)
chmod -R 775 $(pwd)
