#!/usr/bin/env bash

# Generate 500 Random read sff files from any 2 region sff dir
# These are needed for fixtures to do testing
# Region dir needs to just have 2 sff files with *01.sff and *02.sff
rdir=$1

# Directory to hold demultiplexed sff files
demultiplex_by_region='demultiplex_by_region'

# Remove old dir if exists
test -e ${demultiplex_by_region} && rm -rf ${demultiplex_by_region}

if [ "${rdir}x" == "x" ]
then
    echo "Please provide a region dir path"
    exit 1
fi

for i in 1 2
do
    sfffile -pickr 500 -o 500RAND0${i}.sff ${rdir}/*0${i}.sff
    mkdir -p ${demultiplex_by_region}/${i}
    pushd ${demultiplex_by_region}/${i}
    sfffile -s -mcf ../../MidParse.conf ../../500RAND0${i}.sff 2>&1 | tee ../../500RAND0${i}.lst
    popd
done
