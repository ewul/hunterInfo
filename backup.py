# coding: utf-8
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.exceptions import ConnectionError
from elasticsearch.client import SnapshotClient
import datetime
import time

def getSnapshotClient():
	global client
	es = Elasticsearch()
	client = SnapshotClient(es)
	try:
		es.info()
	except ConnectionError, e:
		return False
	return True

while (not getSnapshotClient()):
	print "sleep 10s"
	time.sleep(10)
else:
	try:
		client.get_repository('HI_backup')
	except NotFoundError, e:
		client.create_repository(repository='HI_backup', body={'type':'fs','settings':{'compress':'true','location':'/rl/back'}})

	try:
		client.get(repository='HI_backup', snapshot=str(datetime.date.today()))
	except NotFoundError, e:
		client.create(repository='HI_backup', snapshot=str(datetime.date.today()))
