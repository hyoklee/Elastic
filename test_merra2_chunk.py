#!/usr/bin/env python
import gzip
import zlib
import struct
file_handler=file('f4385663d2ada95b7af245fe262464e5', 'rb')
buf = file_handler.read()
print len(buf)
dec = zlib.decompressobj(32+zlib.MAX_WBITS)
unzipped = dec.decompress(buf)
print len(unzipped)
# 52416
# https://support.hdfgroup.org/ftp/HDF5/tools/h5check/src/unpacked/src/h5pline.c
# https://github.com/OPENDAP/bes/blob/dmr%2B%2B/modules/dmrpp_module/DmrppUtil.cc
# http://blog.omega-prime.co.uk/?p=184
# http://cloudydap.opendap.org:8080/s3/dap/cloudydap/merra2/MERRA2_100.tavgM_2d_int_Nx.198001.nc4.ascii?PRECCU[0:1:0][91:1:91][288:1:288]
# (1.4311204665773403e-07,)
# elems 13104 = 52416 / 4
# 13111 (=elems +7) / 8 = 1638 = duffs_index
# width = 4
# for width {
#   swithch (7) {
#     *_dest = *_src++; _dest += width;
#     *_dest = *_src++; _dest += width;
#   } while (--duffs_index > 0)
# }
a = unzipped[1]+unzipped[13104]+unzipped[26208]+unzipped[39312]
print a
print len(a)
print struct.unpack('<f', a)

