#!/bin/bash
cd /home/marc/Documents/Projects/immo_report/data/classified/

for file in classified_*.json
do
  # Replace ":" with "" in the filename
  newname=${file// /}
  # Rename the file
  mv "$file" "$newname"
done
