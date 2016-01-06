#!/bin/bash
while IFS='' read -r line || [[ -n "$line" ]]; do
    # echo "Indexing file: $line"
    name=${line##* }
    # name=$( echo "$line" | cut -f3 )
    echo $name
    fname=${name##*/}
    echo $fname
    rsync -avzuP publicdata.opensciencedatacloud.org::ark:/31807/osdc-8a052845/$name $fname
    echo $fname.xml
    ~/src/h4map/install/bin/h4mapwriter $fname $fname.xml
    python2.7 h4map_parser.py -f $fname.xml
    rm -f $fname
    rm -rf $fname.xml
done < "$1"

# ~/src/h4map/install/bin/h4mapwriter dem15ARC_E0N0.hdf dem15ARC_E0N0.hdf.xml
# python2.7 h4map_parser.py -f dem15ARC_E0N0.hdf.xml
