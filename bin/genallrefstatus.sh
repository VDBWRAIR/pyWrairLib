#!/usr/bin/env bash

##############################################################################
##  Author: Tyghe Vallard
##  Date: 3/21/2013
##  Email: vallardt@gmail.com
##  Purpose:
##      Given a directory as parameter to this script, this script will
##      find all files called 454RefStatus.txt in that directory.
##      It then loops over all of those files and does the following:
##          echo's the path to 454RefStatus.txt
##          cat the first 2 lines of 454RefStatus.txt
##          cat and sort the rest of 454RefStatus.txt
##  Version:
##      1.0 -
##          Initial Script
##############################################################################


if [ $# -ne 1 ]
then
    echo "Enter a directory to search for 454RefStatus.txt files"
    exit 1
fi

# Very simple script to gather all 454RefStatus.txt into one output that has each file sorted by Ref Name
find $1 -name '454RefStatus.txt' | while read file; do echo ${file}; cat ${file} | head -n 2; cat ${file} | egrep -v '^(Reference|Accession)' | sort; done
