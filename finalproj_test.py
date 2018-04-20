import unittest
from coindesk import *
from redditscrape import *
from coinmktcap import *


class TestDatabase(unittest.TestCase):

	def test_historical_prices(self):
		call_historical_data('Ethereum') #to ensure that if we have not called it before, it will be inserted into the db
		conn = sqlite3.connect('coin_historical_data.db')
		cur = conn.cursor()

		statement = '''
		SELECT Open from Historical_Data
		JOIN Coin
		ON Historical_Data.CoinId=Coin.Id
		WHERE CoinName = 'Ethereum'
		'''
		results = cur.execute(statement)
		result_lst=[]
		for row in results:
			result_lst.append(row)
		
		self.assertEqual(len(result_lst),30)
		self.assertIsInstance((result_lst[0]),tuple)
		self.assertIsInstance((result_lst[0][0]),float)


		conn.close()

	def test_coin_names(self):
		get_coin_names()
		conn = sqlite3.connect('coin_historical_data.db')
		cur = conn.cursor()

		statement = '''
		SELECT CoinName FROM Coin
		'''
		results = cur.execute(statement)
		result_lst=[]
		for row in results:
			result_lst.append(row[0])

		self.assertIn('Bitcoin',result_lst)
		self.assertIn('SpankChain',result_lst)
		self.assertGreater(len(result_lst),1000)

		statement = '''
		SELECT Symbol FROM Coin
		'''
		results = cur.execute(statement)
		result_lst=[]
		for row in results:
			result_lst.append(row[0])

		self.assertIn('BTC',result_lst)
		self.assertEqual(result_lst[1],'ETH')
		self.assertIsInstance(result_lst[12],str)
		self.assertEqual(len(result_lst[0]),3)
		self.assertGreater(len(result_lst),1000)

		conn.close()

	def test_coindesk(self):
		collect_coindesk_news('Bitcoin')
		conn = sqlite3.connect('coin_historical_data.db')
		cur = conn.cursor()

		statement = '''
		SELECT * FROM Coindesk
		JOIN Coin
		ON Coindesk.CoinId = Coin.Id
		WHERE CoinName='Bitcoin'
		'''
		results = cur.execute(statement)
		result_lst=[]
		for row in results:
			result_lst.append(row)

		self.assertTrue(len(result_lst[0]),4)
		self.assertIsInstance(result_lst[0],tuple)
		self.assertIsInstance(result_lst[0][3],str)
		self.assertEqual(int(result_lst[0][1]),1)
		self.assertIsInstance(result_lst[1][2],str)
		conn.close()

	def test_coin_current_info(self):
		results = call_coin_current_info('Ripple')

		self.assertEqual(results[0],'Ripple')
		self.assertEqual(eval(results[1]),3) #Their ranking is subject to change, but not likely to happen within the next month.
		self.assertIsInstance(eval(results[2]),float)

		
unittest.main()
