import utility
import json

def setupTest():
	import search
	with open('setup.json', 'r') as file:
		data=json.load(file)
		print(str(data))
	file.close()
	
def searchDownload():
	import search
	params={'tags': 'dog'}
	search.downloadImages(params, limit=10)
	"""params['geo']={}
	params['geo']['latitude']=35.6582
	params['geo']['longitude']=-83.52"""
	
def dbBasicSetup():
	import imageDB
	#imageDB.addLocalImage('images/flickr41912362032')
	imageDB.addFolder('images')
	
def tagImages():
	import imageDB
	from imageDB import DBQuery
	for image in DBQuery():
		image.tag('test')
	print(imageDB.db.tag_dict)
	"""for image in DBQuery():
		for tag in image.tags():
			print (tag.tagname)"""
	for image in DBQuery():
		for tag in image.tags():
			image.removeTag(tag.tagname)
			image.tag("test2")
	for image in DBQuery():
		for tag in image.tags():
			print(tag.tagname)
	
		
	
if __name__=="__main__":
	#setupTest()
	#searchDownload()
	#dbBasicSetup()
	tagImages()
