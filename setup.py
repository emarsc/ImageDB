import json
import os


if os.path.isfile("setup.json"):
	with open('setup.json', 'r+') as file:
		data=json.load(file)
	file.close()
else:
	data={}
def searchSetup():
	flickr_key=input("Enter flickr api key ")
	search_download_path=input("Enter search download path (folder will be created) ")
	os.makedirs(search_download_path)

	data['flickr_key']=flickr_key
	data['search_download_path']=search_download_path
	with open('setup.json', 'w+') as file:
		json.dump(data, file)
	file.close()
	
def dbSetup():
	data['host']=input("Enter database host address. ")
	data['db_name']=input("Enter database name. ")
	data['user']=input("Enter database username. ")
	data['password']=input("Enter user password. ")
	with open('setup.json', 'w+') as file:
		json.dump(data, file)
	file.close()
	
	
	
	

	
	