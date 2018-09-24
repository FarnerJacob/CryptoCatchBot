#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import csv
import sys
from openpyxl import load_workbook
import openpyxl
from Analyze import analyzeNewTweet
import psycopg2
from Query import createTweetTable, addTweetRow, getTicker

#Twitter API credentials
consumer_key = "REMOVED"
consumer_secret = "REMOVED"
access_key = "REMOVED"
access_secret = "REMOVED"

# Collects the tweet history for a twitter account up to 3200 tweets
def get_all_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	#initialize a list to hold all the tweepy Tweets
	alltweets = []

	#make initial request for most recent tweets (200 is the maximum allowed count)
	username = str(screen_name)
	username = username.strip("()'',")

	while True:
		try:
			new_tweets = api.user_timeline(screen_name = username,count=200)
			break
		except TweepError:
			print('Error avoided. Attempting again...')

	#save most recent tweets
	alltweets.extend(new_tweets)

	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1

	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:

		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = username,count=200,max_id=oldest)

		#save most recent tweets
		alltweets.extend(new_tweets)

		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

	#transform the tweepy tweets into a 2D array that will populate the csv
	outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

	print("%s: %s tweets" % (username, len(alltweets)))

	length = len(outtweets)
	for tweet in outtweets:
		#ws.append(outtweets[length-1])
		addTweetRow(username,outtweets[length-1])
		length-=1
	#wb.save("TweetStorage/"+screen_name+".xlsx")

	pass

# Collects new tweets for twitter account
def getNewTweets(screen_name,latestTweet):
	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	username = str(screen_name)
	username = username.strip("()'',")
	#make initial request for most recent tweets (200 is the maximum allowed count)
	while True:
		try:
			newTweets = api.user_timeline(screen_name = username,since_id=latestTweet)
			break
		except TweepError:
			print('Error avoided. Attempting again...')

	#transform the tweepy tweets into a 2D array that will populate the csv
	outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in newTweets]

	ticker = ""
	if(len(outtweets)>0):
		print("%s: %s tweets" % (username, len(outtweets)))
		ticker = getTicker(username)

	#write the excel
	#wb = load_workbook(filePath)
	#ws = wb.get_active_sheet()
	length = len(outtweets)
	for tweet in outtweets:
		addTweetRow(username,outtweets[length-1])
		#ws.append(outtweets[length-1])
		analyzeNewTweet(outtweets[length-1],ticker)
		length-=1
	#wb.save(filePath)

	pass

if __name__ == '__main__':
	#pass in the username of the account you want to download
	get_all_tweets(sys.argv[1])
