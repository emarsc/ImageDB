from bs4 import BeautifulSoup
import urllib.request
import re
from urllib.error import URLError, HTTPError

def htmlParse(html):

	"""monthDict = {'January': 1,
 		'February': 2,
		 'March': 3,
		 'April': 4,
		 'May': 5,
		 'June': 6,
		 'July': 7,
		 'August': 8,
		 'September': 9,
		 'October': 10,
		 'November': 11,
		 'December': 12,
		}
	i=0
	while i<5:
		i=i+1
		try:
			response=urllib.request.urlopen(url)
		except URLError as e:
			print('Url Error')
			return None
		except HTTPError as e:
			print('HTTP Error')
			return None
		except Exception as e:
			print(e.message)
			return None
		else:
			html=response.read()
			break
	if(i==5):
		print("Check connection")
		return None"""
	#doc = open('test.txt', 'wb')
	#doc.write(html)
	soup = BeautifulSoup(html, 'html.parser')
	imageLink = soup.find("meta", property="og:image")
	#date = soup.find("span", class_ = "date-taken-label")
	#print(imageLink['content'])
	#print(str(date.contents[0]))
	#dateString = r'Taken on (\w+) (\d+), (\d+)\n\t\t'
	#date = re.search(dateString, str(date.contents[0]))
	#print (monthDict[date.group(1)])
	if imageLink  is not None:
		return imageLink['content']
		#return [imageLink['content'], [date.group(3), monthDict[date.group(1)], date.group(2)]]


