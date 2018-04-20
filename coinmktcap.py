import requests
from bs4 import BeautifulSoup
import json
import arrow
import codecs
import sys
import sqlite3

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

DBNAME = 'coin_historical_data.db'


def init_db(db):
	conn = sqlite3.connect(db)
	cur = conn.cursor()



	statement='''
		CREATE TABLE IF NOT EXISTS 'Historical_Data'(
		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
		'CoinId' INTEGER,
		'Open' INTEGER,
		'High' INTEGER,
		'Low'INTEGER,
		'Close' INTEGER,
		'Volume' INTEGER,
		'Market_Cap' INTEGER,
		'Date' TEXT);'''

	cur.execute(statement)

	statement = '''
		CREATE TABLE IF NOT EXISTS 'Coin'(
		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
		'CoinName' TEXT,
		'Symbol' TEXT
		)
	'''
	cur.execute(statement)
	conn.commit()
	conn.close()


#used inside of 'get_coin_names()'
#takes the coins that were retrieved from 'get_coin_names()' and inserts them into the db
def insert_coin_name_data(coin_list):
	conn = sqlite3.connect('coin_historical_data.db')
	cur = conn.cursor()

	for coin in coin_list:
		insertion = (None,coin[0],coin[1])
		statement = 'INSERT INTO "Coin" '
		statement += 'VALUES (?,?,?)'
		cur.execute(statement,insertion)
	conn.commit()
	conn.close()

#Inserts price data for coin of interest
def insert_historical_data(coin_name,historical_list):
	init_db('coin_historical_data.db')
	get_coin_names()

	conn = sqlite3.connect('coin_historical_data.db')
	cur = conn.cursor()

	statement = "SELECT Id FROM Coin "
	statement += "WHERE CoinName = '" + coin_name + "' "
	cur.execute(statement)
	row = cur.fetchone()[0]

	for price in historical_list:
		insertion = (None, row, price['Open'],price['High'],price['Low'],price['Close'],price['Volume'],price['Market Cap'], price['Date'])
		statement = 'INSERT INTO "Historical_Data" '
		statement += 'VALUES (?,?,?,?,?,?,?,?,?)'
		cur.execute(statement,insertion)
		conn.commit()
	conn.close()



#calls coinmktcap for all the coins they have on record and their respective symbol, inserts them into db. Over 1500 coins
def get_coin_names():
	init_db('coin_historical_data.db') #makes tables if there are none
	try:
		conn = sqlite3.connect('coin_historical_data.db')
		cur = conn.cursor()

		statement = "SELECT * FROM Coin"
		cur.execute(statement)
		coin_list = []
		for row in cur:
			name = row[1]
			symbol = row[2]
			ind_coin = [name,symbol]
			coin_list.append(ind_coin)
	

	except:
		pass
	if len(coin_list) < 1000:
		url = 'https://coinmarketcap.com/all/views/all/'
		data = requests.get(url).text
		soup = BeautifulSoup(data,'html.parser')

		coin_list = []
		table = soup.find('tbody')

		rows = table.find_all('tr')

		for row in rows:
			name = row.find(class_='currency-name-container').text.strip()
			symbol = row.find(class_='currency-symbol').text.strip()
			ind_coin = [name.replace(" ", "-"),symbol]
			coin_list.append(ind_coin)
		insert_coin_name_data(coin_list)


	return coin_list


#Retreives current price and 24hr percent change. Does not store to cache for time reasons
def call_coin_current_info(coin):

	baseurl = " https://api.coinmarketcap.com/v1/ticker/"
	try:
		try:
			data = requests.get(baseurl+coin).text
			data = json.loads(data)


			results = (data[0]['name'],
			data[0]['rank'],
			data[0]['price_usd'],
			data[0]['percent_change_24h']
			)
		except:
			data = requests.get(baseurl+coin+"-token").text
			data = json.loads(data)


			results = (data[0]['name'].replace("-token",""),
			data[0]['rank'],
			data[0]['price_usd'],
			data[0]['percent_change_24h']
			)
	except:
		results=("We're Sorry, we cannot find this coin's current price and rank","It looks like this coin stores its information under a pseudonym we did not expect",
			"","")

	return results


#Will call for historical data of the coin and it's price, and return the datapoints
def call_historical_data(coin):
	 #makes the tables if there are none
	test = 0
	try: #connecting and grabbing
		get_coin_names()
		conn = sqlite3.connect('coin_historical_data.db')
		cur = conn.cursor()
		statement = "SELECT * FROM Historical_Data "
		statement += "JOIN Coin ON Coin.id = Historical_Data.CoinId "
		statement += "WHERE CoinName = '" + coin + "' "
		cur.execute(statement)
		historical_list = []
		for row in cur:
			dic = {}
			dic['Open'] = row[2]
			dic['High'] = row[3]
			dic['Low'] = row[4]
			dic['Close'] = row[5]
			dic['Volume'] = row[6]
			dic['Market Cap'] = row[7]
			dic['Date'] = row[8]
			historical_list.append(dic)
		if len(historical_list) >20:
			test = 1
		conn.close()
		
	except:
		pass

	if test == 0:

		try:

			init_db('coin_historical_data.db')
			baseurl = 'https://coinmarketcap.com/currencies/'
			extension_url = '/historical-data/'

			data = requests.get(baseurl+coin+extension_url).text
			soup = BeautifulSoup(data,'html.parser')

			table = soup.find('tbody')
			table = soup.find_all('tr')
			del(table[0])
			historical_list = []

			for point in table:
			
				data_peice = point.find_all('td')
			
			
				dic = {}
				dic['Open'] = data_peice[1].text.strip()
				dic['High'] = data_peice[2].text.strip()
				dic['Low'] = data_peice[3].text.strip()
				dic['Close'] = data_peice[4].text.strip()
				dic['Volume'] = data_peice[5].text.strip()
				dic['Market Cap'] = data_peice[6].text.strip()
				dic['Date'] = data_peice[0].text.strip()
				historical_list.append(dic)

			insert_historical_data(coin,historical_list)

		except:
			init_db('coin_historical_data.db')
			baseurl = 'https://coinmarketcap.com/currencies/'
			extension_url = '/historical-data/'

			data = requests.get(baseurl+coin+"-token"+extension_url).text
			soup = BeautifulSoup(data,'html.parser')

			table = soup.find('tbody')
			table = soup.find_all('tr')
			del(table[0])
			historical_list = []

			for point in table:
			
				data_peice = point.find_all('td')
			
			
				dic = {}
				dic['Open'] = data_peice[1].text.strip()
				dic['High'] = data_peice[2].text.strip()
				dic['Low'] = data_peice[3].text.strip()
				dic['Close'] = data_peice[4].text.strip()
				dic['Volume'] = data_peice[5].text.strip()
				dic['Market Cap'] = data_peice[6].text.strip()
				dic['Date'] = data_peice[0].text.strip()
				historical_list.append(dic)

			insert_historical_data(coin,historical_list)
	return historical_list
