# Distributed processing of subset & aggregation operation on MERRA2.
#
from pyes import *
import urllib2
import zlib
import struct
import sys
from distributed import Client

index_name = 'merra2-monthly'
type_name = 'float32'

conn = ES('127.0.0.1:9200')

# Search
def search(query):
    q = QueryStringQuery(query, default_operator="AND")
    result = conn.search(query=q, indices=[index_name])
    a = []
    for r in result:
        url = get_url(r)
        a.append(url)
    return a

def get_url(r):
    url = 'https://s3.amazonaws.com/cloudydap/bytestream/'+r['md5']
    return url

def compute(url):
    # print url
    response = urllib2.urlopen(url)
    buf = response.read()
    # print len(buf)
    dec = zlib.decompressobj(32+zlib.MAX_WBITS)
    unzipped = dec.decompress(buf)
    # print len(unzipped)
    # Pick a specific point
    a = unzipped[1]+unzipped[13104]+unzipped[26208]+unzipped[39312]
    # print struct.unpack('<f', a)
    return struct.unpack('<f', a)

# a = search("PRECCU AND chunk_position:\[0,0,0\] AND filename:MERRA2_100*")
a = search("PRECCU AND chunk_position:\[0,91,288\] AND filename:MERRA2_100*")
# a = search("PRECCU AND chunk_position:\[0,0,0\] AND filename:*tavgM_2d_int_*")
# search("PRECCU AND chunk_position:\[0,91,288\] AND filename: MERRA2_400.tavgM_2d_int_Nx.201507.nc4")


c = Client('localhost:8786')
m = c.map(compute, a)
x = c.gather(m)
print x
