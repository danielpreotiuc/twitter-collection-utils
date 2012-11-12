#!/bin/bash
BASEDIR=$(pwd)
FILES="$BASEDIR/$1/*"
for f in $FILES
do
  if [ ${f: -4} == ".raw" ]
  then
    tac ${f} | awk '!x[$0]++' | tac > ${f:0:-4}.u
#    lzop -9U ${f:0:-4}.u
    rm $f
    echo "Processed $f"
  fi
done
