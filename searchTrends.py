from TwitterSearch import *
import twitter 
import re
import collections
import csv

try:
    keys = []
    f = open('keys.txt', 'r')
    for key in f:
        keys.append(key.rstrip())
    print keys

    CONSUMER_KEY = keys[0]
    CONSUMER_SECRET = keys[1]
    OAUTH_TOKEN = keys[2]
    OAUTH_SECRET = keys[3]

    twitter = twitter.Twitter(auth = twitter.OAuth(OAUTH_TOKEN, OAUTH_SECRET,
                                            CONSUMER_KEY, CONSUMER_SECRET))
    results = twitter.trends.place(_id = 23424977)
    trendList = []
    for location in results:
            for trend in location["trends"]:
                        trendList.append(trend["name"])
    
    trendList = trendList[:5]
    print trendList

    f = open('trends.txt', 'w')
    for trend in trendList:
        f.write(trend)
        f.write('\n')
    f.close()

    tso = TwitterSearchOrder() 
    tso.set_language('en')
    tso.set_include_entities(False) 

    f = open('tweets.txt', 'w')

    for trend in trendList:    
        tso.set_keywords([trend]) 

        ts = TwitterSearch(
            consumer_key = CONSUMER_KEY,
            consumer_secret = CONSUMER_SECRET,
            access_token = OAUTH_TOKEN,
            access_token_secret = OAUTH_SECRET
        )

    
        for tweet in ts.search_tweets_iterable(tso):
            print(tweet['text'])
            f.write (tweet['text'].encode('utf-8'))
            f.write ('\n')

    f.close()

except TwitterSearchException as e: 
    print(e)

