#
#
from pyes import *
import urllib2
import zlib
import struct
import sys
index_name = 'merra2-monthly'
type_name = 'float32'

conn = ES('127.0.0.1:9200')

# Search
def search(query):
    q = QueryStringQuery(query, default_operator="AND")
    result = conn.search(query=q, indices=[index_name])
    for r in result:
        compute(r)

def compute(r):
    url = 'https://s3.amazonaws.com/cloudydap/bytestream/'+r['md5']    
    # print r['filename']
    # print r._meta.id
    # return
    # print url
    response = urllib2.urlopen(url)
    buf = response.read()
    # print len(buf)
    dec = zlib.decompressobj(32+zlib.MAX_WBITS)
    unzipped = dec.decompress(buf)
    # print len(unzipped)
    # Pick a specific point
    a = unzipped[1]+unzipped[13104]+unzipped[26208]+unzipped[39312]
    print struct.unpack('<f', a)


# search("PRECCU AND chunk_position:\[0,0,0\] AND filename:MERRA2_100*")
search("PRECCU AND chunk_position:\[0,91,288\] AND filename:MERRA2_100*")
# search("PRECCU AND chunk_position:\[0,0,0\] AND filename:*tavgM_2d_int_*")
# search("PRECCU AND chunk_position:\[0,91,288\] AND filename: MERRA2_400.tavgM_2d_int_Nx.201507.nc4")

