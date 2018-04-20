import requests
import json
import sys
import codecs
import webbrowser
import arrow


class rPost():

	def __init__(self, title, url):
		self.title = title
		self.url = url
	def __str__(self):
		return self.title

#Calls the top reddit posts within the hour for the coin of interest
def call_reddit_posts(coin):
	
	url = 'https://www.reddit.com/r/' + str(coin) + '/top/.json'
	data = requests.get(url, headers={'user-agent': 'scraper by /u/tortiees'}).json()
	baseurl = 'https://www.reddit.com'
	data = data['data']['children']
	print(data)
	coin_dict = {}
	coin_dict[str(arrow.now().format('YYYY-MM-DD'))] = {}

	coin_dict[str(arrow.now().format('YYYY-MM-DD'))][str(coin)] = []
	for post in data:
		post_dict = {}
		r_post = rPost(post['data']['title'],str(baseurl + post['data']['permalink']))
		post_dict['title'] = r_post.title
		post_dict['url'] = r_post.url
		coin_dict[str(arrow.now().format('YYYY-MM-DD'))][str(coin)].append(post_dict)


	return coin_dict

#Checks to see whether the coin has been searched within the current day
def try_r_cache(coin):
	test = 0
	try: #see's whether the file exists
		
		fr = open('reddit.json','r')
		data = fr.read()
		coin_dict = json.loads(data)
		fr.close()
		print('fetching cache file...')
		

		#try: #if it does exist, see if and entry for today has been made
			
		if str(arrow.now().format('YYYY-MM-DD')) in coin_dict:
			
			# an entry has been made, now see if the user has searched the coin today
			if str(coin) in coin_dict[str(arrow.now().format('YYYY-MM-DD'))]:
				coin_ = coin_dict[str(arrow.now().format('YYYY-MM-DD'))][str(coin)]
				test = 1 #file exists, set test=1 so it does not itterate through a specific branch
			
			#the user hasn't searched the coin today yet, so we need to make a web request
			else:

				update = call_reddit_posts(str(coin)) #web request
				coin_dict[str(arrow.now().format('YYYY-MM-DD'))].update(update[str(arrow.now().format('YYYY-MM-DD'))]) #updates cache file
			
				json_dumps = json.dumps(coin_dict,indent=3) #formats cache file from dictionary back into json format
				fw = open('reddit.json','w') #opens the file you want to open, if the file doesn't previously exist it will create one
				fw.write(json_dumps) #writes to it
				fw.close()
				coin_ = coin_dict[str(arrow.now().format('YYYY-MM-DD'))][str(coin)]
				test = 1 #file exists, set test=1 so it does not itterate through a specific branch
		#It's a new day!
		else: 
			#havent made an entry today yet, so need to update the date as well as the coin
			coin_dict.update(call_reddit_posts(str(coin)))
			json_dumps = json.dumps(coin_dict,indent=3)
			fw = open('reddit.json','w')
			fw.write(json_dumps)
			fw.close()
			coin_ = coin_dict[str(arrow.now().format('YYYY-MM-DD'))][str(coin)]
			test = 1 #file exists, set test=1 so it does not itterate through a specific branch
		
	except:
		pass

	if test == 0:
	#We have never made an entry before, so need to create from scratch


		coin_dict = call_reddit_posts(str(coin))

		json_dumps = json.dumps(coin_dict, indent=3)
		fw = open('reddit.json','w')
		fw.write(json_dumps)
		fw.close()
		coin_ = coin_dict[str(arrow.now().format('YYYY-MM-DD'))][str(coin)]

	#by now every branch should have a 'coin_' dictionary

	post_list = []


	for post in coin_:
		r_post = rPost(post['title'],post['url'])
		post_list.append(r_post)
	return post_list
#Processes reddit class data and appends to a list 
def produce_post_data(coin):
	data = try_r_cache(coin)
	lst = []

	for post in data:
		postlst = []
		postlst.append(post.title)
		postlst.append(post.url)
		lst.append(postlst)
	if len(lst) < 25:
		while len(lst) != 25:
			postlst=[]
			postlst.append("")
			postlst.append("")
			lst.append(postlst)
	return lst


#user interface on terminal
if __name__ == '__main__':

	command = input('Enter a coin: ')
	print('\n' + '\n')

	activeCoin = []

	while command != 'exit':
		try:
			url = activeCoin[eval(command)-1].url
			webbrowser.open(url)
		except:
			result = (try_r_cache(str(command)))
			index = 1
			active = []
			for post in result:
				print(str(index) + ': ' + post.title)
				index +=1
				active.append(post)
			activeCoin = active
			print('\n' + '\n')
		command = input('Enter article number to open webbrowser, or enter another coin: ')
	print('\n' + '\n')
	
