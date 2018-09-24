import datetime
import psycopg2

conn = psycopg2.connect("dbname='REMOVED' user='REMOVED' password='REMOVED'")

# Adds a new row to the Cryptocurrency table
def addCryptocurrencyRow(ticker, username):
    cur = conn.cursor()
    twitterID = getTwitterID(username)
    cur.execute("Insert into cryptocurrency (ticker, twitterID) values ('"+ticker+"','"+twitterID+"');")
    cur.close()
    conn.commit()

# Adds a new row to the Exchange table
def addExchangeRow(username):
    cur = conn.cursor()
    twitterID = getTwitterID(username)
    cur.execute("Insert into exchange (twitterID) values ('"+twitterID+"');")
    cur.close()
    conn.commit()

# Adds a new row to the KeyWord table
def addKeyWordRow(keyWord):
    cur = conn.cursor()
    cur.execute("Insert into keyWord (keyWord, averagePriceChange) values ('"+keyWord+"',0);")
    cur.close()
    conn.commit()

# Adds a new row to the Notification table
def addNotificationRow(tweetID, type, ticker, estimatedPriceChange):
    cur = conn.cursor()
    cur.execute("Insert into notification (tweetID, type, ticker, estimatedPriceChange) values ('"+tweetID+"','"+type+"','"+ticker+"','"+estimatedPriceChange+"');")
    cur.close()
    conn.commit()

# Adds a new row to the priceAnalysis table
def addPriceAnalysisRow(tweetID, keyWord, priceChange):
    cur = conn.cursor()
    cur.execute("Insert into priceAnalysis (tweetID, keyWord, priceChange) values ('"+tweetID+"','"+keyWord+"','"+priceChange+"');")
    cur.close()
    conn.commit()

# Adds a new row to the Tweet table
def addTweetRow(name, row):
    cur = conn.cursor()
    twitterID = getTwitterID(name)
    id = str(row[0])
    rawDate = row[1]
    refinedDate = rawDate.strftime('%Y-%m-%d %H:%M:%S')
    rawText = str(row[2])
    refinedText = rawText.replace("'","")
    cur.execute("Insert into tweet (ID,CreateTime,Text,twitterID) values ('"+id+"','"+refinedDate+"','"+refinedText[1:]+"',"+twitterID+");")
    cur.close()
    conn.commit()

# Adds a new row to the Twitter table
def addTwitterRow(username):
    cur = conn.cursor()
    cur.execute("Insert into twitter (username) values ('"+username+"');")
    cur.close()
    conn.commit()

# Adds a new row to the WordPair table
def addWordPairRow(firstWord, secondWord):
    cur = conn.cursor()
    cur.execute("Select id from keyWord where keyWord = '"+firstWord+"'")
    firstWord = cur.fetchone()
    firstWord = strip(firstWord)
    cur.execute("Select id from keyWord where keyWord = '"+secondWord+"'")
    secondWord = cur.fetchone()
    secondWord = strip(secondWord)
    cur.execute("Insert into wordPair (firstWord, secondWord, averagePriceChange) values ('"+firstWord+"','"+secondWord+"',0);")
    cur.close()
    conn.commit()

# Creates the Cryptocurrency table
def createCryptocurrency():
    cur = conn.cursor()
    cur.execute("Create table cryptocurrency (twitterID int, ticker varchar(10));")
    cur.close()
    conn.commit()

# Creates the Exchange table
def createExchange():
    cur = conn.cursor()
    cur.execute("Create table exchange (twitterID int);")
    cur.close()
    conn.commit()

# Creates the KeyWord table
def createKeyWord():
    cur = conn.cursor()
    cur.execute("Create table keyWord (ID serial, keyWord varchar(255), averagePriceChange double precision);")
    cur.close()
    conn.commit()

# Creates the Notification table
def createNotification():
    cur = conn.cursor()
    cur.execute("Create table notification (tweetID bigint, type varchar(10), ticker varchar(10), estimatedPriceChange double precision);")
    cur.close()
    conn.commit()

# Creates the priceAnalysis table
def createPriceAnalysis():
    cur = conn.cursor()
    cur.execute("Create table priceAnalysis (tweetID bigint, keyWord varchar(255), priceChange double precision);")
    cur.close()
    conn.commit()

# Creates the Tweet table
def createTweetTable() :
    cur = conn.cursor()
    cur.execute("Create table tweet (ID bigint, CreateTime timestamp, Text text, twitterID int);")
    cur.close()
    conn.commit()

# Creates the Twitter table
def createTwitter():
    cur = conn.cursor()
    cur.execute("Create table twitter (ID serial, username varchar(255));")
    cur.close()
    conn.commit()

# Creates the WordPair table
def createWordPair():
    cur = conn.cursor()
    cur.execute("Create table wordPair (firstWord int, secondWord int, averagePriceChange double precision);")
    cur.close()
    conn.commit()

# Drops the specified table from the database
def dropTable(name):
    cur = conn.cursor()
    cur.execute("Drop table if exists "+name)
    cur.close()
    conn.commit()

# Gets all the tweets from the twitter account
def getAllTweets(username):
    cur = conn.cursor()
    twitterID = getTwitterID(username)
    cur.execute("Select * from tweet where twitterID = "+twitterID)
    return cur

# Gets the estimated price change for the specified keyword
def getEstimatedPriceChange(keyword):
    cur = conn.cursor()
    cur.execute("Select averagePriceChange from keyword where keyword = '"+keyword+"'")
    result = cur.fetchone()
    result = strip(result)
    result = round(float(result), 2)
    return str(result)

# Gets the list of keyword from the database
def getKeyWords():
    cur = conn.cursor()
    cur.execute("Select keyWord from keyWord where keyword not in (' is ', ' now ')")
    return cur

# Gets the last tweet collected for the twitter account
def getLatestTweetID(name):
    cur = conn.cursor()
    name = str(name)
    username = name.strip("''(),")
    twitterID = getTwitterID(username)
    cur.execute("Select ID from tweet where twitterID = '"+twitterID+"' order by ID desc limit 1")
    result = cur.fetchone()
    result = str(result)
    result = result.strip("(),")
    return result

# Gets the ticker associated with the twitter account
def getTicker(name):
    cur = conn.cursor()
    twitterID = getTwitterID(name)
    cur.execute("Select ticker from cryptocurrency where twitterID = '"+twitterID+"'")
    result = cur.fetchone()
    if(result is None):
        return None
    result = str(result)
    result = result.strip("()'',")
    return result

# Gets the twitter ID for the twitter account
def getTwitterID(username):
    cur = conn.cursor()
    cur.execute("Select ID from twitter where username = '"+username+"'")
    result = cur.fetchone()
    result = str(result)
    result = result.strip("(),")
    return result

# Gets the list of all twitter accounts
def getTwitter():
    cur = conn.cursor()
    cur.execute("Select username from twitter")
    return cur

# Gets word pairs for the specified word
def getWordPairs(word):
    cur = conn.cursor()
    cur.execute("Select id from keyWord where keyword = '"+word+"'")
    wordID = cur.fetchone()
    wordID = strip(wordID)
    cur.execute("Select secondWord from wordPair where firstword = '"+wordID+"'")
    secondWordIDList = cur.fetchall()
    wordPairList = []
    if(len(secondWordIDList)>0):
        for ID in secondWordIDList:
            cur.execute("Select keyWord from keyWord where id = '"+strip(ID)+"'")
            tmp = cur.fetchone()
            tmp = strip(tmp)
            wordPairList.append(tmp)
    return wordPairList

# Strips the string of any unnecessary characters
def strip(word):
    word = str(word)
    word = word.strip("()'',")
    return word

# Updates the average KeyWord price change
def updateKeyWordPercent(word):
    cur = conn.cursor()
    cur.execute("Select priceChange from priceAnalysis where keyWord = '"+word+"'")
    percentList = cur.fetchall()
    totalPercent = 0
    numberOfPercents = len(percentList)
    for percent in percentList:
        percent = str(percent)
        percent = percent.strip("(),")
        if(float(percent)<1000):
            totalPercent+=float(percent)
        else:
            numberOfPercents-=1
    averagePercent = totalPercent/numberOfPercents
    cur.execute("Update keyWord set averagePriceChange = '"+str(averagePercent)+"' where keyWord = '"+word+"'")

# Updates the average WordPair price change
def updateWordPairPercent(word, wordPair):
    cur = conn.cursor()
    cur.execute("Select id from keyWord where keyWord = '"+word+"'")
    wordID = cur.fetchone()
    wordID = strip(wordID)
    cur.execute("Select id from keyWord where keyWord = '"+wordPair+"'")
    wordPairID = cur.fetchone()
    wordPairID = strip(wordPairID)
    concatenatedWord = word+", "+wordPair
    cur.execute("Select priceChange from priceAnalysis where keyWord = '"+concatenatedWord+"'")
    percentList = cur.fetchall()
    totalPercent = 0
    numberOfPercents = len(percentList)
    for percent in percentList:
        percent = strip(percent)
        if(float(percent)<1000):
            totalPercent+=float(percent)
        else:
            numberOfPercents-=1
    averagePercent = totalPercent/numberOfPercents
    cur.execute("Update wordPair set averagePriceChange = '"+str(averagePercent)+"' where firstWord = '"+wordID+"' and secondWord = '"+wordPairID+"'")
