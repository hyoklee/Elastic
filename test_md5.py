#!/usr/bin/env python

import gzip
import zlib
# 400x1200 chunk uint8
offset = 23560
length = 488
#  different md5 value
# offset = 16894
# length = 488

# Read offset length from file and decompress.
file_handler=file('MOD17A3H.A2014001.h35v10.006.2015295055317.hdf',"rb")
file_handler.seek(offset)
buf = file_handler.read(length)
dec = zlib.decompressobj(32+zlib.MAX_WBITS)
unzipped = dec.decompress(buf)
newfile = open('2014.bin', 'wb')
newfile.write(unzipped)


# 400x1200 chunk int16
offset2 = 15913
length2 = 953
file_handler2=file('MOD17A3H.A2005001.h35v10.006.2015113010954.hdf',"rb")
file_handler2.seek(offset2)
buf2 = file_handler2.read(length2)
dec2 = zlib.decompressobj(32+zlib.MAX_WBITS)
unzipped2 = dec2.decompress(buf2)
newfile2 = open('2015.bin', 'wb')
newfile2.write(unzipped2)

