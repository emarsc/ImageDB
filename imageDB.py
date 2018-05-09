import setup
import os
import utility
import database
from database import DB
import json
from PIL import Image


if not os.path.isfile('setup.json'):
	setup.dbSetup()
	
db=DB()

with open('setup.json', 'r') as file:
	data=json.load(file)
file.close()
if 'host' not in data.keys():
	setup.dbSetup()
	with open('setup.json', 'r') as file:
		data=json.load(file)
	file.close()

db.connect(data['host'], data['db_name'], data['user'], data['password'])

def addLocalImage(file_path, tags=None, metadata={}):
	if file_path.split(".")[-1]!='jpg' and file_path.split(".")[-1]!="png":
		print(str(file_path.split(".")))
		print("Invalid file path")
		return -1
	metadata['source']='local'
	metadata['file_path']=file_path
	metadata['tags']=tags
	db.addImage(**metadata)
	
def addFolder(folder_path, tags=None, metadata={}):
	if list(folder_path)[-1]!='/':
		folder_path=folder_path+'/'
	file_paths=os.listdir(folder_path)
	for path in file_paths:
		addLocalImage(folder_path+path, tags=tags, metadata=metadata)


class Tag:

	def __init__(self, tagname, tagdata):
		self.tagname=tagname
		self.tagdata=tagdata
	
class ImageMeta:

	def __init__(self, meta):
		self.metadata=meta
		self.id=meta['id']
		
	def image(self):
		if self.metadata['file_path'] is not None:
			return Image.open(self.metadata['file_path'])
		elif self.metadata['url'] is not None:
			return utility.imageFromUrl(self.metadata['url'])
		return -1
		
	def tag(self, tagname, tagdata=None):
		db.tagImage(self.id, tagname)
		
	def removeTag(self, tagname):
		db.unTagImage(self.id, tagname)
		
	def remove(self):
		db.removeImage(self.id)
	
	def tags(self):
		tags=[]
		query_result=db.getImageTags(self.id)
		#print(query_result)
		for row in query_result:
			tags.append(Tag(row['tagname'], row['tag_data']))
		return tags
		
		
class DBQuery:
	
	def __init__(self, tags=[], limit=100000):
		self.query_result=db.getImages(tags=tags)
		#print(str(self.query_result))
		self.index=-1
		
	def __iter__(self):
		return self
	
	def __next__(self):
		self.index+=1
		if self.index==len(self.query_result):
			raise StopIteration
		else:
			return ImageMeta(self.query_result[self.index])
		
		
	

	

