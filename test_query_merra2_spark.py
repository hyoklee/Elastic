from __future__ import print_function

import sys
from random import random
from operator import add
from pyes import *
import urllib2
import zlib
import struct
import sys


from pyspark.sql import SparkSession


if __name__ == "__main__":
    """
        Usage: ./bin/spark-submit --master spark://nene:7077 ~/src/Elastic/test_query_merra2_spark.py
    """
    spark = SparkSession\
        .builder\
        .appName("ElasticMerra2")\
        .getOrCreate()


    def search(query):
        conn = ES('127.0.0.1:9200')
        index_name = 'merra2-monthly'
        type_name = 'float32'
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

    a = search("PRECCU AND chunk_position:\[0,91,288\] AND filename:MERRA2_100*")    
    count = spark.sparkContext.parallelize(a).map(compute).reduce(add)
    spark.stop()
    print(count)

