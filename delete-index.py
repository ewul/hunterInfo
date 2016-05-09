from elasticsearch import Elasticsearch

es = Elasticsearch()
es.indices.delete(index='hunter-data', ignore=[400, 404])
