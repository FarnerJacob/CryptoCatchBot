from CryptoCompare import get_historical_price, get_histo_minute, get_histo_hour
from datetime import timedelta
from datetime import timezone
import datetime
import time as Time
import psycopg2
import re
import threading
from twilio.rest import Client
from pynput import keyboard
from firebase import firebase
from Query import getKeyWords, getTwitter, getAllTweets, getEstimatedPriceChange, getTicker, createPriceAnalysis, addNotificationRow,addPriceAnalysisRow, updateKeyWordPercent, updateWordPairPercent, getWordPairs, dropTable

# Analyzes all collected tweets for keywords and pairs to find the average price change
def analyzeOldTweets():
    twitterList = getTwitter()
    for username in twitterList:
        username = str(username)
        username = username.strip("()'',")
        if(not close):
            analyzeAllTweets(username)
            print()
        else:
            break

# Analyzes all tweets of the twitter account
def analyzeAllTweets(username):
    tweets = getAllTweets(username)
    print(username)
    tweets = tweets.fetchall()
    for tweet in tweets:
        if(not close):
            text = str(tweet[2])
            text = text.strip("()'',")
            text = text.lower()
            findKeyWords(text, tweet, username)
        else:
            break

# Searches the tweet for any keywords
def findKeyWords(text, tweet, username):
    keyWords = getKeyWords()
    for word in keyWords:
        word = str(word)
        word = word.strip("()'',")
        if(text.find(word)>=0):
            if(tweet[0]!=844549929829912576):
                percentChange = analyzeByHourPrice(tweet, username)
                if(percentChange is not None and percentChange!=0):
                    addPriceAnalysisRow(str(tweet[0]), word, str(percentChange))
                    findWordPairs(str(tweet[0]), text, word, percentChange)
                    updateKeyWordPercent(word)

# Finds the ticker in the tweet's text
def findTicker(text):
    searchObj = re.search( r'.*\(([A-Z]{2,5})\).*', text, re.M|re.I)
    if(searchObj):
        result = searchObj.group(1)
        if(result=='CNY' or result=='USD' or result=='iOS' or result=='Bull' or result=='beta' or result=='Mobi'):
                return None
        return result.upper()
    searchObj = re.search( r'.*#([A-Z]{2,5})\s.*', text, re.M|re.I)
    if(searchObj):
        result = searchObj.group(1)
        if(result=='CNY' or result=='USD' or result=='iOS' or result=='Bull' or result=='beta' or result=='Mobi'):
                return None
        return result.upper()
    searchObj = re.search( r'.*\$([A-Z]{2,5}).*', text, re.M|re.I)
    if(searchObj):
        result = searchObj.group(1)
        if(result=='CNY' or result=='USD' or result=='iOS' or result=='Bull' or result=='beta' or result=='Mobi'):
                return None
        return result.upper()
    return None

# Searches if there are any word pairs in the tweet
def findWordPairs(tweetID, text, word, percentChange):
    wordPairs = getWordPairs(word)
    for wordPair in wordPairs:
        wordPair = str(wordPair)
        wordPair = wordPair.strip("()'',")
        if(text.find(wordPair)>=0):
            addPriceAnalysisRow(tweetID, word+", "+wordPair, str(percentChange))
            updateWordPairPercent(word, wordPair)

# Helper variable to count the number of requests sent to CryptoCompare
numberOfRequests = 0
# Analyzes the price increase by the hour of cryptocurrency
def analyzeByHourPrice(tweet, username):
    ticker = getTicker(username)
    if(ticker is None):
        ticker = findTicker(tweet[2])
    if(ticker is None):
        return None

    #global numberOfRequests
    #numberOfRequests+=1
    #print(numberOfRequests)

    print(ticker+": "+str(tweet[0]))
    data = get_histo_hour(ticker, tweet[1])
    data = data['Data']
    startPrice = 0
    counter = 0
    if(len(data)!=0):
        while(startPrice==0):
            startPrice = data[counter]['open']
            counter+=1
        highestPrice = startPrice
        if(startPrice==0):
            return None
        else:
            for hour in range(counter,len(data)):
                if(data[hour]['high']>highestPrice):
                    highestPrice = data[hour]['high']
            percentChange = ((highestPrice-startPrice)/startPrice)*100
            return percentChange
    else:
        print(tweet[2])
        return None

# Analyzes a new tweet for the estimated price change
def analyzeNewTweet(tweet, ticker):
    time = str(tweet[1])
    keyWords = getKeyWords()
    message = str(tweet[2])
    message = message.lower()
    # Searches the tweet for every keyword
    for word in keyWords:
        word = str(word)
        word = word.strip("()'',")
        if(message.find(word)>=0):
            estimatedPriceChange = getEstimatedPriceChange(word)
            # If there is no ticker associated with the twitter account, it will attempt to find the ticker in the tweet text
            if(ticker is None):
                ticker = findTicker(message)
            if(float(estimatedPriceChange)>0):
                message = str(tweet[2])
                message = message[2:]
                message = message[:-1]
                time = Time.mktime(Time.strptime(time, '%Y-%m-%d %H:%M:%S'))
                # Adds a notification for a tweet when a ticker is found
                if(ticker is not None):
                    addNotificationRow(tweet[0],'Buy',ticker,estimatedPriceChange)
                    upload(ticker,message,estimatedPriceChange, time)
                    pushNotification('Buy '+ticker+' with an estimated price increase of '+estimatedPriceChange+'%. This notification is in response to this tweet: '+message)
                # Adds a notification for a tweet when a ticker is not found
                else:
                    addNotificationRow(tweet[0],'Buy','?',estimatedPriceChange)
                    upload('?',message,estimatedPriceChange, time)
                    pushNotification('A ticker could not be found, but a tweet associated with an estimated percent increase of '+estimatedPriceChange+'. This notification is in response to this tweet: '+message)
            print("The word, "+word+", was detected.")

# Gets the price of a cryptocurrency at a specified time
def getPriceHistory(ticker, time):
    return get_historical_price(ticker, 'USD', time)

# Sends a text notification for a potential trading opportunity
def pushNotification(message):
    client = Client('REMOVED','REMOVED')
    client.messages.create(from_='REMOVED',
                       to='REMOVED',
                       body=message)

# Uploads the notification to Firebase
def upload(ticker, tweet, estimatedPriceChange, time):
    fire = firebase.FirebaseApplication('REMOVED', None)
    data = {'ticker': ticker, 'tweet': tweet, 'estimatedPriceChange': estimatedPriceChange, 'time': time}
    fire.post('/notifications', data)


# This adds the ability to stop Analyze.py from running when started
c = threading.Condition()
def on_press(key):
    try:
        global close
        c.acquire()
        close = True
        print("Shutting down...")
        c.notify_all()
        c.release()
        return False
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('Shutting down...'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

close = False
# Main method that recreates the priceAnalysis table and analyzes all tweets
if __name__ == '__main__':
    dropTable('priceAnalysis')
    createPriceAnalysis()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    analyzeOldTweets()
