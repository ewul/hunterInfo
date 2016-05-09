from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from elasticsearch import Elasticsearch
import json
from django.views.decorators.csrf import csrf_exempt
import uuid

es = Elasticsearch()

# Create your views here.
def home(request):
	newflag = request.GET.get('new','0')
	return render_to_response('home.html', {"newflag":newflag})
	
def duplicate(request):
	return render(request, 'duplicate.html')

def duplicateExpand(request):
	uid = request.GET.get('uid','')
	return render(request, 'duplicateExpand.html')
	
def search(request):
	query = request.GET.get('query','')
	if query.strip()=='':
		body={
			"query": {
				"bool": {
				  "must": [
					{
						"match_all": {
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
			"size": 100
		}
	else:
		body={
			"query": {
				"bool": {
				  "must": [
					{
						"query_string": {
							"default_field": "_all",
							"query": query
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
			"size": 100
		}

	esres = es.search(
		index='hunter-data',
		doc_type='resume',
		body=body
	)
	res = []
	for hit in esres['hits']['hits']:
		resume={}
		resume.update({'uid':hit['_id']})
		resume.update({'name':hit['_source']['name']})
		resume.update({'company':hit['_source']['company']})
		resume.update({'comments':hit['_source']['comments']})
		resume.update({'telnos':' '.join(hit['_source']['telnos'])})
		resume.update({'location':hit['_source']['location']})
		resume.update({'position':hit['_source']['position']})
		resume.update({'updatedate':hit['_source']['updatedate']})
		if hit['_source'].has_key('email'):
			resume.update({'email':hit['_source']['email']})
		res.append(resume)

	return HttpResponse(json.dumps(res), content_type="application/json")

@csrf_exempt
def edit(request):
	res={}
	uid=request.POST['form[uid]']
	if uid == '':
		uid = str(uuid.uuid1())
		resume={}
		res.update({'method':'new', 'uid':uid})
	else:
		resume=es.get(index='hunter-data',doc_type='resume',id=uid)['_source']
		res.update({'method':'update', 'uid':uid})
	resume.update({'name':request.POST['form[name]']})
	resume.update({'company':request.POST['form[company]']})
	resume.update({'comments':request.POST['form[comments]']})
	resume.update({'telnos':[request.POST['form[telnos]']]})
	resume.update({'location':request.POST['form[location]']})
	resume.update({'position':request.POST['form[position]']})
	resume.update({'updatedate':request.POST['form[updatedate]']})
	resume.update({'email':request.POST['form[email]']})
	resume.update({'status': ''})
	resume.update({'delete': 0})
	resume.update({'duplicateAnalyse': 0})
	es.index(index='hunter-data',doc_type='resume',id=uid,body=resume)
	return HttpResponse(json.dumps(res), content_type="application/json")

@csrf_exempt
def delete(request):
	uid=request.POST['form[uid]']
	if uid != '':
		es.delete(index='hunter-data',doc_type='resume',id=uid)
	return HttpResponse(json.dumps({'uid':uid}), content_type="application/json")
