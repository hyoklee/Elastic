#!/bin/bash
for fname in MOD13C2*.hdf
do
    ~/bin/h4mapwriter -ftmu $fname $fname.xml	
done
