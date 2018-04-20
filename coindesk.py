import requests
from bs4 import BeautifulSoup
import json
import sys
import codecs
import sqlite3


#Called articles from coindesk for coin of interest
def collect_coindesk_news(coin):
	baseurl = "https://www.coindesk.com/"
	params = {
	"s" : str(coin)
	}
	try:
		results = requests.get(baseurl, params=params).text
		soup = BeautifulSoup(results,"html.parser")

		#get urls of pages
		pages = soup.find(class_='pagination')
		pages = pages.find_all('a',href=True)
		page_links = []
		for link in pages:
			page_links.append(link['href'])
				

		pages_object = []

		#append the first page to the object list
		content = soup.find_all(id="content")
		content = content[0].find_all(class_="post-info")
		pages_object.append(content)
		#append the rest of the url soup objects
		for url in page_links:
			results = requests.get(url).text
			soup = BeautifulSoup(results,'html.parser')
			content = soup.find_all(id="content")
			content = content[0].find_all(class_="post-info")
			pages_object.append(content)

		
		dict_info = {}

		data_list=[]
		
		for contents in pages_object:
			titles_list=[]
			for post in contents:
				titles = post.find('h3')
				titles_list.append(titles)
		
			for title in titles_list:
				post_dict = {}
				post_dict['title'] = title.text.strip()
				url = title.find('a',href=True)
				post_dict['url'] = url['href']
				data_list.append(post_dict)



		dict_info[coin] = data_list
		insert_data(dict_info,coin)
	except:
		dict_info={}
	return dict_info



def try_using_cache(coin):
	create_db_table()
	try:
		try:
			
			fr = open('coindesk_cache.json','r')
			data = fr.read()
			news_dict = json.loads(data)
			fr.close()
			
			if str(coin) in news_dict:
				
				return news_dict[str(coin)]
			else:
			
				info = collect_coindesk_news(str(coin))
				insert_data(info[str(coin)],coin)
				news_dict.update(info)
		except:
		
			news_dict = collect_coindesk_news(str(coin))

		fw = open('coindesk_cache.json','w')
		data = json.dumps(news_dict,indent=3)
		fw.write(data)
		fw.close()
		return news_dict[str(coin)]
	except:
		lst = []
		return lst


def create_db_table():
	conn = sqlite3.connect('coin_historical_data.db')
	cur = conn.cursor()

	statement = '''
		CREATE TABLE IF NOT EXISTS 'Coindesk'(
		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
		'CoinId' INTEGER,
		'Article_Title' TEXT,
		'URL' TEXT);
	'''
	cur.execute(statement)
	conn.commit()
	conn.close()

def insert_data(data,coin_name):
	create_db_table()
	conn = sqlite3.connect('coin_historical_data.db')
	cur = conn.cursor()
	statement = "SELECT Id FROM Coin WHERE CoinName = '" + coin_name + "' "
	cur.execute(statement)
	row = cur.fetchone()[0]
	
	for instance in data[coin_name]:
		insertion = (None, row, instance['title'],instance['url'])
		statement = 'INSERT INTO "Coindesk" '
		statement += 'VALUES (?,?,?,?)'
		cur.execute(statement,insertion)
	conn.commit()
	conn.close()




