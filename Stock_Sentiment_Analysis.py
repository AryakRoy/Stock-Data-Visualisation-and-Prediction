from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

class Sentiment_Analyzer:
    def __init__(self):
        self.finviz_url = r"https://finviz.com/quote.ashx?t="

    def Analysis(self,ticker):
        parsed_data = []
        news_dict = {}
        url = self.finviz_url + ticker
        req = Request(url = url, headers = {'user-agent' : 'my-app'})
        response = urlopen(req)
        html = BeautifulSoup(response, 'html.parser')
        news = html.find(id = 'news-table').findAll('tr')
        headers = [i.a.text for i in news]
        times = [i.td.text for i in news]
        for index, time in enumerate(times):
            date_data = time.split(' ')
            if( len( date_data) == 2):
                date = date_data[0]
                time = date_data[1]
                news_dict[date] = []
            else : 
                time = date_data[0]
            news_dict[date].append([time, headers[index]])
            parsed_data.append([ date, time, headers[index]])   
        return self.Sentiment(parsed_data)

    def Sentiment(self,table):
        df = pd.DataFrame(table, columns = ['Date', 'Time', 'Headline'])
        vader = SentimentIntensityAnalyzer()
        pol_scores = []
        for i in df['Headline']:
            pol_scores.append(vader.polarity_scores(i)['compound'])
        import statistics
        m = statistics.mean(pol_scores)
        if m == 0.0:
            return 'No Change'
        elif m > 0 and m <= 0.5 :
            return 'Upwards 📈'
        elif m > 0.5 : 
            return 'Highly Upwards 📈'
        elif m < 0 and m >= -0.5 : 
            return 'Downwards 📉'
        else : 
            return 'Highly Downwards 📉'