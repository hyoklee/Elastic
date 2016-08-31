#!/usr/bin/env python
import struct
import requests
import gzip
import zlib
from StringIO import StringIO
url = "http://localhost/oco2_L2StdND_03945a_150330_B6000_150331024816.h5"

# Retrieve bytes.
r = requests.get(url, headers={"range": "bytes=108875990-108877075"})
# print r.content
dec = zlib.decompressobj(32+zlib.MAX_WBITS)
unzipped = dec.decompress(r.content)
print struct.unpack('>b', unzipped[0])



