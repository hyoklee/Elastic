# time wget 'http://localhost:8080/opendap/data/hdf4/MOD08_M3.A2014335.006.2015035022023.hdf.dods?Solar_Zenith_Mean_Mean'

time wget 'http://localhost:8080/opendap/data/hdf4/MOD08_M3.A2014335.006.2015035022023.hdf.dods?Solar_Zenith_Mean_Mean,Solar_Zenith_Mean_Std'

time wget 'http://giraffe:8080/opendap/data/hdf4/MOD08_M3.A2014335.006.2015035022023.hdf.das'

# HDF5 ascii
time curl -g -O 'http://giraffe:8080/opendap/data/NASAFILES/hdf5/oco2_L2StdND_03945a_150330_B6000_150331024816.h5.ascii?L1bScSoundingReference_packaging_qual_flag[0:1:0][0:1:0]'

# HDF5 binary
time curl -g -O 'http://giraffe:8080/opendap/data/NASAFILES/hdf5/oco2_L2StdND_03945a_150330_B6000_150331024816.h5.dods?L1bScSoundingReference_packaging_qual_flag[0:1:0][0:1:0]'