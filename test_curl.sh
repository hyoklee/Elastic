#!/bin/bash
# HDF4 File Content Maps used.
# [1] https://eosdap.hdfgroup.org:8887/thredds/h4map/mnt/ftp/pub/outgoing/NASAHDF/3B43.070901.6A.HDF 
# [2] https://eosdap.hdfgroup.org:8887/thredds/h4map/mnt/ftp/pub/outgoing/NASAHDF/MOD08_M3.A2014335.006.2015035022023.hdf

# Retrieve multiple byte ranges.
# time curl -r '294-297,298-301' http://localhost/3B43.070901.6A.HDF

# Retrieve entire precipitation dataset -  offset="294" nBytes="2304000"
# time curl -r '294-2304294' http://localhost/3B43.070901.6A.HDF -o test.bin

# Retrieve entire dataset from [2].
time curl -r '310-58521' http://localhost/MOD08_M3.A2014335.006.2015035022023.hdf -o test.bin

# Retrieve two datasets from [2].
time curl -r '310-58521,58537-109801' http://localhost/MOD08_M3.A2014335.006.2015035022023.hdf -o test.bin

# Retrieve scale_factor attribute.
time curl -r '36756687-36756694' http://localhost/MOD08_M3.A2014335.006.2015035022023.hdf -o test.bin

# Compare byte-range vs entire file transfer.
time curl http://localhost/test.bin -o test2.bin

# Test Tomcat server.
time curl -r '294-2304294' http://localhost:8889/3B43.070901.6A.HDF -o test.bin

# Test HDF5 file.
time curl -r '108875990-108877075' http://localhost/oco2_L2StdND_03945a_150330_B6000_150331024816.h5 -o test.bin