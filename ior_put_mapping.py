# pip install elasticsearch
import json
from elasticsearch import Elasticsearch

# Connect.
es = Elasticsearch(cloud_id="HPF:********", http_auth=('elastic','********'))
print(es.info())
print(es.indices.delete(index='ior-index'))
print(es.indices.create(index='ior-index', ignore=400))
data = {
    'properties': {
        'date': {'type': 'date',
                 'format': 'EEE MMM dd HH:mm:ss yyyy'
        },
        'host': {'type': 'text',
                 'fields': {
                     'keyword': {
                         'type': "keyword",
                         "ignore_above": 256
                     }
                 }                     
        },
        'name': {'type': 'text',
                 'fields': {
                     'keyword': {
                         'type': "keyword",
                         "ignore_above": 256
                     }
                 }                     
        },
        'result': {'type': 'float'},
        'version': {'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': "keyword",
                            "ignore_above": 256
                        }
                    }                                             
        },
    }
}
# print(data)
print(es.indices.put_mapping(index="ior-index", body=data))
