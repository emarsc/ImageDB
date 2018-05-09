#Handles database queries
#02/12/18

import pymysql.cursors
import atexit
import datetime	
import json

filter={'min_date': 'date_taken>%s',
		'max_date': 'date_taken<%s',
		'year': 'YEAR(date_taken)=%s',
		'month': 'MONTH(date_taken)=%s',
		'day_of_year': 'DAYOFYEAR(date_taken)=%s',
		'date_taken': 'date_taken=%s',
		'region': 'images.region LIKE %s',
		'geo_range': 'ST_WITHIN(images.gps, ST_BUFFER(POINT%s, %s))' 
		}

def makeFilter(params, union=False):
	#constructing a sql 'WHERE' clause using the database schema and the params passed in
	#this is for selecting from images table
	#input: params=array of tuples of the form [(<param_key>, <value>),...]
	#output: sql, [values]
	#geo_range=[<(x, y)>, <radius>] 
	if (len(params))==0:
		return "", []
	sql="WHERE" #string used to execute query
	values=[] #values order matches ordering of respective '%s' in sql string
	condition=" "
	for param in params:
		sql=sql+condition+filter[param[0]]
		if param[0]=='geo_range':
			values.extend(param[1])
		else:
			values.append(param[1])
		condition=' AND '
		if union:
			condition=' OR '
	return sql, values
	
class DB():
	#Access and update database

	def connect(self, host, dbname, user, pswd):
		#connecting to database
		self.connection=pymysql.connect(
			host=host, 
			user=user,
			password=pswd,
			db=dbname,
			cursorclass=pymysql.cursors.DictCursor)					
		self.cursor=self.connection.cursor()
		self.tag_dict=self.getTags()
		atexit.register(self.connection.close)
		
	def query(self, sql, values=None):
		if values is None:
			self.cursor.execute(sql)
		else:
			self.cursor.execute(sql, values)
		self.connection.commit()
		return self.cursor.fetchall()
		
	
	def addImage(self, source, source_id=None, url=None, file_path=None, date_taken=None, gps=None, latitude=None, longitude=None, imagehash=None, tags=None):
		if (url is None and file_path is None):
			print("Failed to add image. There must be a reference to the image location (file_path or url required)")
			return -1
		if gps is not None:
			point_str="POINT%s"
		else:
			point_str="%s"
		sql="INSERT IGNORE INTO images (source, source_id, url, file_path, date_taken, gps,  latitude, longitude, imagehash) VALUES (%s, %s, %s, %s, %s, "+point_str+", %s, %s ,%s)"
		self.query(sql, values=(source, source_id, url, file_path, date_taken, gps, latitude, longitude, imagehash))	
		if tags is not None: #Poor runtime in some cases
			image_id=self.query("SELECT LAST_INSERT_ID()")[0]["LAST_INSERT_ID()"]
			self.tagImage(image_id, tags)
		return 1
	
	def removeImage(self, image_id):
		self.query(sql="DELETE FROM tag_links WHERE image_id=%s", values=(image_id))
		self.query(sql="DELETE FROM images WHERE image_id=%s", values=(image_id))

	def addImages(self, image_dicts):
		#adds array of image dictionaries to database
		for image in image_dicts:
			self.addImage(**image)

	def createTag(self, tagname):
		print(str(self.tag_dict))
		self.query("INSERT IGNORE INTO tags (tagname) values (%s)", values=(tagname))
		self.tag_dict=self.getTags()
		print(str(self.tag_dict))
		return self.tag_dict[tagname]

	def tagImage(self, image_id, tagname, tag_data=None, tag_value=None):
		if tagname not in self.tag_dict.keys():
			print("Creating tag: '"+tagname+"'")
			self.createTag(tagname)
		tag_id=self.tag_dict[tagname]
		if tag_data is not None:
			tag_data=json.dumps(tag_data) #converting to json string
		values=(image_id, tag_id, tag_data, tag_value)
		sql="REPLACE INTO tag_links (image_id, tag_id, tag_data, tag_value) VALUES (%s, %s, %s, %s)"
		self.query(sql, values=values)
		return 1
		
	def unTagImage(self, image_id, tagname):
		self.query(sql="DELETE FROM tag_links WHERE tag_id=%s and image_id=%s", values=(self.tag_dict[tagname], image_id))
	
	#---Simple/Necessary Queries---
	
	def getImages(self, selection='*', filter_params=[], order_by='date_taken', limit=100000, union=False, tags=[]):
		#returns images based on filter_params. See makeFilter()
		#default arguments return (max)100000 images in database ordered by date_taken
		limit="LIMIT "+str(limit)
		where_clause, values=makeFilter(filter_params, union=union)
		i=0
		while i<len(tags):
			if tags[i] not in self.tag_dict.keys():
				print("'"+tags[i]+"' does not exist. Ignoring tag")
				tags.pop(i)
			else:
				i+=1
		join=""
		for tagname in tags:
			tag_id=self.tag_dict[tagname]
			values.insert(0, tag_id)
			join=join+"INNER JOIN tag_links ON tag_links.tag_id=%s AND tag_links.image_id=images.id "
		sql="SELECT "+selection+" FROM images "+join+where_clause+" ORDER BY "+order_by+" "+limit
		values=tuple(values)
		return self.query(sql, values=values)
		
	def getImageTags(self, image_id):
		return self.query(sql="SELECT * FROM (SELECT * FROM tag_links WHERE image_id=%s) s INNER JOIN tags ON tags.id=s.tag_id", values=(image_id))
		
	
	def getTags(self):
		#returns a tag dictionary of all tags.  {<tag_name>: tag_id, ...}
		tags=self.query("SELECT * FROM tags")
		tag_dict={}
		for t in tags:
			tag_dict[t['tagname']]=t['id']
		return tag_dict	
	
	
	def exists(self, table_name, column, column_value):
		sql="SELECT 1 FROM %s WHERE %s=%s"
		if self.query(sql, values=(table_name, column, column_value)):
			return True
		return False
		
	def pruneIDs(self, id_list):
		#checking to see which ids are already in database
		if(len(id_list))<1:
			return None
		values=[]
		#id_list is list of values of form (id, source)
		sql="SELECT search.id, search.source FROM (SELECT %s AS id, %s AS source "
		values.extend([id_list[0][0], id_list[0][1]])
		for i in range(1, len(id_list)):
			sql=sql+"UNION ALL SELECT %s, %s "
			values.extend([id_list[i][0], id_list[i][1]])
		sql=sql+") search LEFT JOIN images ON search.id=images.source_id AND search.source LIKE images.source WHERE images.id is null"
		rows=self.query(sql, values=tuple(values))
		pruned_ids=[]
		for row in rows:
			pruned_ids.append((row['id'], row['source']))
		return pruned_ids
		#----------------------------------------
		
		#-------Analytical Queries---------------
		
	def getTagParams(self, tagname):
		if tagname not in self.tag_dict.keys():
			self.tag_dict=self.getTags()
			if tagname not in self.tag_dict.keys():
				print("Tag not found.")
				return -1
		tag_id=self.tag_dict[tagname]
		sql="SELECT STDDEV(tag_value) as stddev, AVG(tag_value) as mean FROM tag_links WHERE tag_id=%s"
		result=self.query(sql, values=(tag_id))
		return result[0]['stddev'], result[0]['mean']

	#----------Update queries--------
	def updateImage(self, image_id, attribute, new_value):
		sql="UPDATE TABLE images SET %s=%s WHERE image_id=%s"
		self.query(sql, values=(attribute, new_value, image_id))
		
"""class SQL: #Class to format sql queries (unsure if this is needed yet)

	in_circle="ST_WITHIN(gps, ST_BUFFER(POINT%s, %s))=1"
	
	def formatWhere(param_dict):
		sql="WHERE"
		andstring=""
		values=[]
		for key in param_dict.keys():
			
			sql=sql+" "+andstring+key
			if(isinstance(param_dict[key], str)):
				sql=sql+" LIKE %s"
				values.append(key)
			elif key!="gps" and key!="radius":
				sql=sql+"=%s"
				values.append(key)
			else:
				sql=sql+" "+in_circle
				values.extend([param_dict['gps'], param_dict['radius']])
			andstring="and "
		return sql, values
		
			
			
	def select(table, attributes=['*'], where={}):
		#Simple select statement. Not useable for joining or complex queries in general
		sql="SELECT "+attributes[0]
		for i in range(1, len(attributes)):
			sql=sql+", "+attributes[i]
		where_clause, values=formatWhere(where)
		sql=" FROM "+table+" "+where_clause
		return sql, values"""
	

		
