import json
import plotly
import plotly.graph_objs as go
import coinmktcap as coincap
import redditscrape as reddit
import sys
from flask import Flask, render_template, flash, request
import coindesk as coindesk

app = Flask(__name__)

coincap.get_coin_names()



@app.route('/',methods=['GET', 'POST'])
def search():

    coin_list = coincap.get_coin_names()

    coin_names = []
    for coin_ in coin_list:
        if "." not in coin_[0]:
            coin_names.append(coin_[0])
    if request.method=='POST':
        global coin
        coin = request.form['coin']
        return coin_info(coin)
    else:
        coin = ""
    return render_template('search.html', coin_names=coin_names,coin=coin)

@app.route('/<coin>',methods=['GET', 'POST'])
def coin_info(coin):

    try: #Retrieves coin names from coin market cap
        coin_list = coincap.get_coin_names()

        coin_names = []
        for coin_ in coin_list:
            coin_names.append(coin_[0])


        if str(coin) in coin_names:
            #Retrieves the current information of the coin
            current_info = coincap.call_coin_current_info(coin)
            currentprice = current_info[2]
            currentrank = current_info[1]
            currentchange = current_info[3]
            try:
                currentprice = str(round(eval(currentprice),2))
                currentchange = str(round(eval(currentchange),2))
            except: 
                #looks like we couldn't retreive this coin's current info
                pass
            
            #Retreives top reddit posts for the coin
            try:
                link_list=[]
                reddit_list = reddit.produce_post_data(coin.replace("-", ""))
                
                for post in reddit_list:

                    lst = []
                    lst.append(post[0])
                    lst.append(post[1])
                    link_list.append(lst)
                
                if len(link_list)==0:
                    
                    for i in range(26):
                        lst=[]
                        lst.append("")
                        lst.append("")
                        link_list.append(lst)
            except:
                link_list=[]
                for i in range(26):
                    lst=[]
                    lst.append("")
                    lst.append("")
                    link_list.append(lst)
            


            #Retreives posts from coindesk.com
            coindesk_ = coindesk.try_using_cache(coin)
            coindesk_list = []
            for post in coindesk_:
                lst =[]
                url = post['url']
                title = post['title']
                lst.append(title)
                lst.append(url)
                coindesk_list.append(lst)

            coindesk_list=list(reversed(coindesk_list))
            list_ = coindesk_list[0:25]
            index =0
            while index != 25:
                try:
                    for post in link_list:
                        list_[index].append(post[0])
                        list_[index].append(post[1])
                        index +=1
                except:
                    index =25


            coin_info = coincap.call_historical_data(coin)
            x0 = []
            y0 = []

            for datapc in coin_info:
                y0.append(datapc['Open'])
                x0.append(datapc['Date'])
            x0 = list(reversed(x0))
            y0 = list(reversed(y0))



            #This graph returns the prices for the coin in the last 30 days.
            graphs = [dict(                                                                   #graph1
                data = [go.Scatter(

                        x = x0,
                        y = y0,
                        line = dict(color = 'rgb(85,255,85')
                )],

                layout = dict(
                    title='1-Month Chart',
                    titlefont=dict(color='rgb(255,255,255'),
                    yaxis=dict(title="Price(USD)",
                        showgrid=False,
                        titlefont=dict(color='rgb(255,255,255'),
                        tickfont=dict(color='rgb(255,255,255')),
                    xaxis=dict(showgrid=False, 
                        tickfont=dict(color='rgb(255,255,255')),
                    paper_bgcolor = 'rgb(21,21,21)',
                    plot_bgcolor = 'rgb(21,21,21)'
                    )
            )
            ]
            ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
            graphJSON = json.dumps(graphs,cls=plotly.utils.PlotlyJSONEncoder)
            print('graph')

            return render_template('coin.html',ids=ids,graphJSON=graphJSON,
                coin=coin,currentchange=currentchange,currentprice=currentprice,currentrank=currentrank,
                list_=list_)

        else:
            return render_template('404.html')
    except:
        #the coin info is named in such a way that each site I try to extract it from does something special to it (they call it something different). example: iExec-RLC
        return render_template('404.html')
if __name__ == '__main__':
    app.run(debug=True)

