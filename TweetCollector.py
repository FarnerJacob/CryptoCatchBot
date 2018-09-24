from tweet_dumper import get_all_tweets, getNewTweets
from openpyxl import load_workbook
from Query import getTwitter, addTwitterRow, createTwitter, getLatestTweetID, createTweetTable
import psycopg2

# Retrieves the tweet history of all twitter accounts in the database (this works for a fresh tweet table; it will add duplicate data if used twice)
def getTweetHistory():
    createTweetTable()
    cur = getTwitter()
    for name in cur.fetchall() :
        get_all_tweets(name)

# Collects new tweets for a specific twitter account
def collectTweets(twitter):
    myConnection = psycopg2.connect("dbname='REMOVED' user='REMOVED' password='REMOVED'")
    latestTweet = getLatestTweetID(twitter)
    getNewTweets(twitter, latestTweet)
