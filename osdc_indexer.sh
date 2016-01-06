# rsync -avzuP publicdata.opensciencedatacloud.org::ark:/31807/osdc-8a052845/ladsweb/LandSeaMask_DEM/6/dem15ARC_E0N0.hdf dem15ARC_E0N0.hdf
# ~/src/h4map/install/bin/h4mapwriter dem15ARC_E0N0.hdf dem15ARC_E0N0.hdf.xml
python2.7 h4map_parser.py -f dem15ARC_E0N0.hdf.xml
