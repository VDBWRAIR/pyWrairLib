#!/bin/bash

## This could be a precursor to automating the 454 demultiplexing and linking

if [ "${1}x" == "x" ]
then
    echo "You need to supply a D_ directory as a parameter"
    exit 1
fi

# First see if we can find the D_ directory given
dpath=$(find . -maxdepth 3 -type d -name "$1")
ddir=$(basename $dpath)
if [ "${dpath}x" == "x" ]
then
    echo "I don't think $dpath exists anywhere"
    echo "I could not find it"
    exit 1
else
    echo "Found $dpath"
fi

# Get the rdir name
rdir=$(basename $(dirname $dpath))

# Get the date from the inputted D_ directory path
pdate=$(echo $ddir | egrep -o '[0-9]{4}_[0-9]{2}_[0-9]{2}')
cd ${pdate}
if [ $? -ne 0 ]
then
    # now try the R_ directory date
    pdate=$(echo $rdir | egrep -o '[0-9]{4}_[0-9]{2}_[0-9]{2}')
    cd ${pdate}

    # FAIL!
    if [ $? -ne 0 ]
    then
        echo "Could not determine correct date for ${1}"
        echo "Apparently this date is not correct ->${pdate}<-"
        exit 1
    fi
fi

# Make the meta and link it into the signal processing directory
mkdir meta
echo "meta directory created"

ln -s $(pwd)/meta ${rdir}/*signal*/
cd ${rdir}/*signal*/
if [ $? -ne 0 ]
then
    ln -s $(pwd)/meta ${rdir}/*full*/
    cd ${rdir}/*full*/
    echo "meta directory linked into full processing dir"
else
    echo "meta directory linked into signal processing dir"
fi

# Link the D_ into the ReadData dir
ln -s $(pwd) /home/EIDRUdata/NGSData/ReadData/Roche454/
echo "D_ directory linked into ReadData"

# Make modifications to runfile if needed(user has to do this)
echo "You will now need to manually move the runfile into the meta directory and make any fixes to it"
echo "Dropping you into a shell at $(pwd)"
echo "Type exit when you are finished moving and setting up the Runfile"
bash

# Demultiplex and link reads
runfile=$(find meta/ -type f -name "Runfile*")
echo "Demultiplexing and linking reads using ${runfile}"
demultiplex -s sff -r ${runfile} && link_reads
if [ $? -ne 0 ]
then
    # Let user fix what went wrong
    echo "Something failed during demultiplexing and linking reads"
    echo "Dropping you into a shell so you can manually fix it"
    echo "You should be able to issue demultiplex -s sff -r ${runfile} && link_reads"
    echo "Type exit when you are finished demultiplexing and linking reads"
    bash
fi

# Replace D_ in old directory structure with the new one
dst=$(grep $(basename $(pwd)) /home/EIDRUdata/Data_seq454/procdirs.lst)
if [ "${dst}x" != "x" ]
then
    echo "Replacing ${dst} with a link to the new data"
    rm -rf $dst
    ln -s $(pwd) $dst;
    echo "${dst} replaced sucessfully"
fi

echo "Completed ${1}"
