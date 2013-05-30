#!/usr/bin/env bash

# Useful Vars
this_dir=$(cd $(dirname 0) && pwd)
pypathdir=$(dirname $(dirname $(dirname $this_dir) ) )
ngspath=$(pwd)/NGSData
midparsepath=$(pwd)/fixtures/MidParse.conf
analysispath=$(pwd)/Analysis
origsettingspath=../../config/settings.cfg
settingspath=$(pwd)/settings.cfg
origrunfilepath=$(pwd)/fixtures/RunfileFlxPlus_2013_05_01.txt
runfilepath=$(pwd)/RunFile.txt
refpath=$(pwd)/fixtures/ref.fna

# Get settings file setup
sed -e "s%NGSDATA_DIR = '.*'%NGSDATA_DIR = '${ngspath}'%" -e "s%MIDPARSEDEFAULT =.*%MIDPARSEDEFAULT = '${midparsepath}'%" -e "s%ANALYSIS_DIR =.*%ANALYSIS_DIR = '${analysispath}'%" $origsettingspath > $settingspath
grep $(whoami) /etc/passwd | awk -F':' '{printf("%s %s\n",$3,$4)}' | while read uid gid
do
    sed -i -e "s/Owner =.*/Owner = $uid/" -e "s/Group =.*/Group = $gid/" $settingspath
done

# Set Up
deactivate
export PYTHONPATH=${pypathdir}/pyWrairLib:${pypathdir}/pyRoche:${pypathdir}/NGSCoverage
_OLDPATH=$PATH
export PATH=${pypathdir}/pyWrairLib/bin:${pypathdir}/pyRoche/bin:${pypathdir}/NGSCoverage/bin:$PATH

# Main goodness

# Setup RunFile
sed "s%User_defined_Reference%${refpath}%" $origrunfilepath > $runfilepath

# Create directories
create_ngs_structure -c ${settingspath}
mkdir $analysispath

demultiplexpath=${ngspath}/ReadData/Roche454/1979_01_01/demultiplexed
test $? -eq 0 && demultiplex -o ${demultiplexpath} --mcf ${midparsepath} -s fixtures/ -r ${runfilepath}
test $? -eq 0 && link_reads -d ${demultiplexpath} -c $settingspath
cd ${analysispath}
test $? -eq 0 && mapSamples.py ${runfilepath} -c $settingspath
ret=$?
cd ..
test $ret -eq 0

# Tear Down
read -p "Tear down temp files/dirs[yn]? " yn
if [ "${yn}" == "y" ]
then
    rm *.log
    rm -rf ${ngspath}
    rm -rf ${analysispath}
    rm ${runfilepath}
    rm $settingspath
    unset PYTHONPATH
    export PATH=$PATH
fi
