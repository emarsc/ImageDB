#utility functions

def pipeData(start_data, functions,  numthreads, buffer_size=10):
		#function to multithread data pipeline through <functions>
		#functions=ordered array of functions with output of function[i] = input of function [i+1]
		#numthreads[i]=number of threads for functions[i]
		#buffer_size=size of buffer to passed from one function to the next
		
		from multiprocessing import Process, Queue
		import atexit
		import time
		
		processes=[]
		def killProcesses():
			for proc in reversed(processes):
				if proc.is_alive():
					proc.terminate()
					print('terminated')
				
		atexit.register(killProcesses)
		
		def subProc(function, data_in, data_out):
			#process function to be called. data in=input queue,  data_out=output queue
			output=[]
			while True:
				if not data_in.empty():
					data=data_in.get()
					if data=='terminate': #close thread
						break
					output=function(data)
					data_out.put(output)
				else:
					time.sleep(1) #So the queue isn't slowed down by constant reading
			data_out.put('terminate') #telling the next thread to terminate
		
		#splicing start_data into buffers
		buffers=[start_data[i:i+buffer_size] for i in range(0, len(start_data), buffer_size)] 
		del start_data[:]
		
		#putting buffers into starting queue
		data_in=Queue()
		for buff in buffers:
			data_in.put(buff)
			
		for i in range(0, numthreads[0]):
			#putting the terminate signal at the end of queue
			data_in.put('terminate')
			
		#defining processes. 	
		for i in range(0, len(functions)):
			data_out=Queue()
			for j in range(0, numthreads[i]):
				processes.append(Process(target=subProc, args=(functions[i], data_in, data_out,)))
			data_in=data_out
			
		#starting threads.	
		for proc in processes:
			proc.start()
		#joining threads
		for proc in processes:
			proc.join()
			
def download(url, file_path):
	import urllib.request
	from urllib.error import URLError, HTTPError
	i=0
	while i<5:
		i=i+1
		try:
			urllib.request.urlretrieve(url, file_path)
		except URLError as e:
			print('Url Error')
		except HTTPError as e:
			print('HTTP Error')
		else:
			return
		
def downloadWithExif(image_dict, file_path):
	import piexif	
	fp=file_path.split(".")
	if fp[-1]!='jpg':
		file_path=file_path+'.jpg'
	try:
		download(image_dict['url'], file_path)
	except Exception as e:
		print("Error: "+str(e))
		return
	print(file_path)
	exif_dict={}
	exif_dict['Exif']={}
	if 'latitude' in image_dict.keys():
		exif_dict['Exif'][piexif.ExifIFD.UserComment]=str((image_dict['latitude'], image_dict['longitude'])) #dumping gps into user comment
	#TODO: add legitimate exif tags for all metadata
	exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]=image_dict['date_taken'].strftime("%Y-%m-%d %H:%M:%S")
	exif_bytes=piexif.dump(exif_dict)
	piexif.insert(exif_bytes, file_path)
			
def getImage(image_dict):
	from PIL import Image
	try:
		download(image_dict['url'], 'getimage.jpg')
		return Image.open('getimage.jpg')
	except Exception as e:
		print("Error: "+str(e))	

def imageFromUrl(url):
	from PIL import Image
	import requests
	from io import BytesIO
	response = requests.get(url)
	img = Image.open(BytesIO(response.content))
	return img

