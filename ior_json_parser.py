# pip install elasticsearch
import json
from elasticsearch import Elasticsearch

# Connect.
es = Elasticsearch(cloud_id="HPF:********", http_auth=('elastic','********'))
print(es.info())

# Create index.
# print(es.indices.create(index='ior-index', ignore=400))

# Import JSON.
try:
    # fname = 'ior-2019-228.json'
    fname = 'ior-2019-229.json'    
    with open(fname) as data_file:
        try:
            source = json.load(data_file)
            print(source)
            
            data = {}
            data['date'] = source['Began']
            data['name'] = source['summary'][0]['operation']
            data['host'] = source['Machine']
            data['version'] = source['tests'][0]['Options']['apiVersion']
            data['result'] = source['summary'][0]['MeanTime']
            print(data)
            print(es.index(index="ior-index", id=3, body=data))
            data2 = {}
            data2['date'] = source['Began']
            data2['name'] = source['summary'][1]['operation']
            data2['host'] = source['Machine']
            data2['version'] = source['tests'][0]['Options']['apiVersion']
            data2['result'] = source['summary'][1]['MeanTime']
            print(data2)
            print(es.index(index="ior-index", id=4, body=data2))
        except ValueError:
            print('ERROR:Invalid json file')
except IOError:
    print('ERROR:cannot open ' + fname)
