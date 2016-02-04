#!/usr/bin/env bash

if ! [[ $1 =~ ^(minted|csvtable|csvtable2)$ ]]; then
	echo "Usage:"
	echo "    create_files <test>"
	echo
	echo "Options:"
	echo "    <test>   The test that should be run: minted, csvtable, csvtable2."
	exit -1
fi

filter=([minted]=./minted.py  [csvtable]=./csvtable.py [csvtable2]=./csvtable.py)

if [ "$(uname)" == "Darwin" ]; then
    location=`dirname $(greadlink -f $0)`
else
    location=`dirname $(readlink -f $0)`
fi


cd $location/..

pandoc -t json -s $location/$1_original.md |\
 python -m json.tool --sort-keys |\
 tee $location/$1_original.json |\
 ${filter[$1]} |\
 python -m json.tool --sort-keys |\
 tee $location/$1_result.json |\
 pandoc -f json -t latex --biblatex -o $location/$1_result.tex
