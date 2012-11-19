#!/bin/bash
BASEDIR=$(pwd)
FILES="$BASEDIR/$1/*"
for f in $FILES
do
  tac ${f} | awk '!x[$0]++' | tac > ${f:0:-4}.u
  rm $f
  echo "Processed $f"
done
