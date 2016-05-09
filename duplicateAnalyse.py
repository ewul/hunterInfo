# coding: utf-8
from elasticsearch import Elasticsearch
import re
import redis
import uuid
import sys
import time
import copy

reload(sys)
sys.setdefaultencoding( "utf-8" )

es = Elasticsearch()
r = redis.Redis()

def putInRedis(hitsData):
	r.set(str(uuid.uuid1()),hitsData)
	r.save()
	

def getDataFromES():
	
	res = es.search(
		index='hunter-data',
		doc_type='resume',
		body={
			"query": {
				"bool": {
				  "must": [
					{
						"range": {
							"duplicateAnalyse": {
							  "lte": "0"
							}
						}
					},
					{
						"range": {
							"delete": {
								"lte": "0"
							}
						}
					}
				  ]
				}
			},
			"from": 0,
			"size": 1000
		}
	)
	
	return res

def parseMatchData(esResponseData):
	if isinstance(esResponseData,dict):
		if esResponseData.has_key('hits'):
			if esResponseData.get('hits').has_key('hits'):
				return esResponseData.get('hits').get('hits')
	return []

def searchForDuplicateData(hitData):
	if hitData.has_key('_source'):
		if hitData.get('_source').has_key('telnos'):
			for fulltelno in hitData.get('_source').get('telnos'):
				if re.search('\d{2} \d{11}',fulltelno):
					pos = re.search('\d{11}',fulltelno).span()
					telno = fulltelno[pos[0]:pos[1]]
					duplicateRes = es.search(
						index='hunter-data',
						doc_type='resume',
						body={
							"query": {
								"bool": {
								  "must": [
									{
										"match": {
											"telnos": telno
										}
									},
									{
										"range": {
											"delete": {
												"lte": "0"
											}
										}
									}
								  ]
								}
							}
						}
					)
					duplicateHitsData = parseMatchData(duplicateRes)
					if len(duplicateHitsData) > 1:
						originalDate = time.strptime(hitData['_source']['updatedate'],'%m/%d/%Y')
						for data in duplicateHitsData:
							contrastDate = time.strptime(data['_source']['updatedate'],'%m/%d/%Y')
							if originalDate != contrastDate:
								if originalDate > contrastDate:
									esDeleteData = copy.deepcopy(data['_source'])
									esDeleteData.update({'duplicateAnalyse': 1})
									esDeleteData.update({'delete': 1})
									esId = copy.deepcopy(data['_id'])
									es.index(index='hunter-data',doc_type='resume',id=esId,body=esDeleteData)
								if originalDate < contrastDate:
									esDeleteData = copy.deepcopy(hitData['_source'])
									esDeleteData.update({'duplicateAnalyse': 1})
									esDeleteData.update({'delete': 1})
									esId = copy.deepcopy(hitData['_id'])
									es.index(index='hunter-data',doc_type='resume',id=esId,body=esDeleteData)
							else:
								#putInRedis(duplicateHitsData)
								esDeleteData = copy.deepcopy(data['_source'])
								esDeleteData.update({'duplicateAnalyse':1})
								esId = copy.deepcopy(data['_id'])
								es.index(index='hunter-data',doc_type='resume',id=esId,body=esDeleteData)
					else:
						esDeleteData = copy.deepcopy(hitData['_source'])
						esDeleteData.update({'duplicateAnalyse':1})
						esId = copy.deepcopy(hitData['_id'])
						es.index(index='hunter-data',doc_type='resume',id=esId,body=esDeleteData)
				else:
					esDeleteData = copy.deepcopy(hitData['_source'])
					esDeleteData.update({'duplicateAnalyse':1})
					esId = copy.deepcopy(hitData['_id'])
					es.index(index='hunter-data',doc_type='resume',id=esId,body=esDeleteData)


esResponseData = parseMatchData(getDataFromES())
while len(esResponseData) > 0:
	for hitData in esResponseData:
		searchForDuplicateData(hitData)
	esResponseData = parseMatchData(getDataFromES())
	print 'process number:'+str(len(esResponseData))
	

