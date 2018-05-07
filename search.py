#master search class.  Inherits all API query functions.

import flickrsearch
import time
import json
import setup
import utility
import os

if not os.path.isfile('setup.json'):
	setup.searchSetup()

with open("setup.json", 'r') as file:
	data=json.load(file)
	flickrsearch.key=data['flickr_key']
	download_path=data['search_download_path']
file.close()

#apis={}
apis={'flickr': flickrsearch} #api modules
#TODO:
"""if twittersearch.authenticated:
	apis['twitter']=twittersearch
apis['fivepx']=fivepxsearch"""


			

def search(p, limit=None):
	params=p
	#Using API services to search a given area
	#params={paramname: param, ...}
	#params={'lat': <latitude>, 'lon': <longitude>, 'radius': <radius>}
	ids=[]
	for api in apis.keys():
		source_ids=apis[api].searchIds(params, limit)
		if limit is not None:
			limit = limit-len(source_ids)
		ids.extend([(source_ids[i], api) for i in range(0, len(source_ids))])
	return ids

def compileData(ids):
	#compiling metadata for given ids. ids=[(idnum, source)....]
	#Returning array of images' metadata ready to be committed to database
	data=[] 
	for id in ids:
		image_data=apis[id[1]].processID(id[0])
		if len(id)>2:
			image_data['tags']=id[2]
		if image_data != -1:
			data.append(image_data)
		#print(str(data[-1]))
	return data
	
def downloadImages(p, path=download_path, limit=None):
	params=p
	print('searching...')
	ids=search(p, limit)
	metadata=compileData(ids)
	print('downloading...')
	if list(path)[-1]!='/':
		path=path+'/'
	for image_meta in metadata:
		file_path=path+image_meta['source']+image_meta['id']
		utility.download(image_meta['url'], file_path)
	
"""def compileData_thread(ids, numthreads=4):
	#Using multiple threads to compile metadata.
	#Significantly faster than single thread version
	from multiprocessing import Process, Queue
	def thread(inputq, resultq):
		while not inputq.empty():
			id=inputq.get()
			resultq.put(apis[id[0]].processID(id[1]))
	inputq=Queue()
	resultq=Queue()
	for api in ids.keys():
		for id in ids[api]:
			inputq.put((api, id)) #(source, id) Example: ('flickr', 21323243)
	processes=[]
	for i in range(0, numthreads):
		p=Process(target=thread, args=(inputq, resultq,))
		processes.append(p)
		p.start()
	while not inputq.empty():
		time.sleep(5)
		print(str(inputq.qsize()))
	time.sleep(5)
	for p in processes:
		p.terminate()
	print('t')
	data=[]
	while not resultq.empty():
		data.append(resultq.get())
	return data"""

if __name__=='__main__':
	print("Search parameters:")
	params={}
	tags=input("Enter space seperated list of tags (Or 'enter' for no tags). ")
	if tags!="":
		params['tags']=tags
	geo=input("Enter <latitude> <longitude> <radius> for geo search (Or 'enter' for no geo parameters). ")
	if geo != "":
		params['geo']={}
		[latitude, longitude, radius]=geo.split(" ")
		params['geo']['latitude']=float(latitude)
		params['geo']['longitude']=float(longitude)
		params['geo']['radius']=float(radius)
	limit=int(input("Enter number of images to download (Or 'enter' for maximum). "))
	if limit=="":
		limit=None
	path=input("Enter file path for download (Or 'enter' for default file path). ")
	if path=="":
		path=download_path
	downloadImages(params, path, limit)
