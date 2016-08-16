from pyes import *

index_name = 'myang64'
type_name = 'nested'

conn = ES('127.0.0.1:9200')

# Search
def search(query):
    q = QueryStringQuery(query, default_operator="AND")
    result = conn.search(query=q, indices=[index_name])
    for r in result:
        print r

search("_FillValue")
