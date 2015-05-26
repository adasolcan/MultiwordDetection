from TwitterSearch import *
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

    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.set_keywords(['country', 'state']) # let's define all words we would like to have a look for
    tso.set_language('en') # we want to see German tweets only
    tso.set_include_entities(False) # and don't give us all those entity information

    # it's about time to create a TwitterSearch object with our secret tokens
    ts = TwitterSearch(
        consumer_key = CONSUMER_KEY,
        consumer_secret = CONSUMER_SECRET,
        access_token = OAUTH_TOKEN,
        access_token_secret = OAUTH_SECRET
    )

    f = open('tweets.txt', 'w')
     # this is where the fun actually starts :)
    for tweet in ts.search_tweets_iterable(tso):
        print(tweet['text'])
        f.write ( tweet['text'].encode('utf-8'))
        f.write ( '\n' )

    f.close();

except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)
