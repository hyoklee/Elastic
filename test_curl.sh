#!/bin/bash
# HDF4 Map:
# https://eosdap.hdfgroup.org:8887/thredds/h4map/mnt/ftp/pub/outgoing/NASAHDF/3B43.070901.6A.HDF 


# Retrieve multiple byte ranges.
# time curl -r '294-297,298-301' http://localhost/3B43.070901.6A.HDF

# Retrieve entire precipitation dataset -  offset="294" nBytes="2304000"
time curl -r '294-2304294' http://localhost/3B43.070901.6A.HDF -o test.bin

