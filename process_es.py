# coding: utf-8
import os
import shutil
import xlrd
import copy
import uuid
import sys
import time
from elasticsearch import Elasticsearch
reload(sys)
sys.setdefaultencoding( "utf-8" )

root=os.path.split(os.path.realpath(__file__))[0]

def getDataProto(titleRow):
	dataProto = {}
	for titleCell in titleRow:
		dataProto.update({titleCell.lower().replace(' ','').replace('.',''):''})
	return dataProto

def getData(datalist, dataProto, dataRow, titleRow):
        if dataRow == titleRow:
			return
	for pos in range(0,len(titleRow)):
		if str(titleRow[pos]) == 'Status':
			position = pos
	if str(dataRow[position]).strip() != '':
		#status cell is not null, means that this data is not additional data
		data = copy.deepcopy(dataProto)
		for i in range(0,len(titleRow)):
			key = str(titleRow[i]).lower().replace(' ','').replace('.','')
			if str(dataRow[i]).strip() != 'N/A':
				if key == 'telnos':
					data.update({key:[str(dataRow[i]).replace("+","").replace("-"," ").strip()]})
				else:
					data.update({key:str(dataRow[i])})
		datalist.append(data)
	else:
		data = datalist[len(datalist)-1]
		#status cell is null, means that this data is additional data, need to be merge to last data
		for i in range(0,len(titleRow)):
			key = str(titleRow[i]).lower().replace(' ','').replace('.','')
			if str(dataRow[i]).strip() != '' and str(dataRow[i]).strip() != 'N/A' :
				if key == 'telnos':
					oldValueArray = data.get(key,[])
					oldValueArray.append(str(dataRow[i]).replace("+","").replace("-"," ").strip())
					data.update({key:oldValueArray})
				else:
					oldValue = data.get(key, '')
					data.update({key:oldValue + ' ' + str(dataRow[i])})
		datalist[len(datalist)-1] = data

def indexToEs(data):

	es = Elasticsearch()
	
	uid = str(uuid.uuid1())
	data.pop('')
	data.update({'duplicateAnalyse':0})
	data.update({'delete':0})
	time.sleep(0.01)
	es.index(index='hunter-data',doc_type='resume',id=uid,body=data)


def getWorkbook(path):
	workbook = xlrd.open_workbook(path)
	for worksheet in workbook.sheets():
		datalist = []
		dataProto = getDataProto(worksheet.row_values(9))
		for i in range(10,worksheet.nrows):
			getData(datalist,dataProto,worksheet.row_values(i),worksheet.row_values(9))
		for data in datalist:
			indexToEs(data)

es = Elasticsearch()
es.indices.create(index='hunter-data', ignore=400)

for rt,dirs,files in os.walk(root+"/data"):
	for file in files:
		print 'processing '+root+'/data/'+file
		getWorkbook(root+'/data/'+file)
		if not os.path.exists(root+'/complete/'):
			os.makedirs(root+'/complete/')
		shutil.move(root+'/data/'+file, root+'/complete/'+file)
