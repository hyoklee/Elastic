#!/usr/bin/env python
import struct
import requests

url = "http://localhost/3B43.070901.6A.HDF"

# Retrieve bytes between offsets 294 and 2304293(inclusive).
r = requests.get(url, headers={"range": "bytes=294-2304293"})

# Comment out the followng lines to measure download time only.
for chunk in r.iter_content(chunk_size=4):
     if chunk:
        print struct.unpack('>f', chunk)




