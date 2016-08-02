#!/usr/bin/env python
import struct
import requests

url = "http://localhost/3B43.070901.6A.HDF"

# Retrieve bytes between offsets 294 and 297 (inclusive).
r = requests.get(url, headers={"range": "bytes=294-297"})
print struct.unpack('>f', r.content)



