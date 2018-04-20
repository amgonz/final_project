Data sources used:
Coindesk.com - A reputable source for cryptocurrency articles
Reddit.com - Where the cryptocurrency community lives and breathes
Coinmarketcap.com - The go-to for cryptocurrency coins, prices, and historical data

Code structure:
Each python file (except for app.py) contains code 
that retrieves/scrapes data from a different data source.
Most noted:
1. call_historical_data(coin)
	- From coinmktcap.py
	- Takes the coin of interest and uses it as an input for scraping 
	historical prices

2. call_reddit_posts(coin)
	- From reddit.com
	- calls the top reddit posts within the hour for the coin of interest

3. collect_coindesk_news(coin)
	- From coindesk.com
	-Called articles from coindesk for coin of interest, scraping through
	many pages

In app.py, the function that does all the brute work is coin_info(coin).
In this function, all data functions are called and processed for jinja2 
to read.


How to Run:
simply enter 'python app.py' and go to the local 
host address in your web browser

Options for searching for coins:
Once you land on the main page, you can either type in your
coin of interest, or you can click one of the coins under the
search bar.
If you choose to type your coin, do note that caps
to matter (i.e. 'Bitcoin', not 'bitcoin')

If you're using brand new cache/db, allow some time
for it to collect all the information.

Once you have loaded a page, it will only take a few seconds to
reload, since it will be able to retreive everything from either
cache or db, depending on the data type.

The only data peice that gets retrieved every time a page is loaded
is the current price, rank, and 24hr change of the coin.
The code for this retreival can be found in coinmktcap.py,
function call_coin_current_info(coin)


Try typing in a nonexistant coin (e.g. 'qwertyasdf')
-You will land on a 404 page, that then directs you back to the main page


Enjoy :)



