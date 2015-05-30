import tweepy

keys = []
with open('keys.txt') as stream:
	keys = [line.strip() for line in stream]
[consumer_key, consumer_secret, access_token, access_token_secret] = keys


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

US_WOEID = '23424977'

response = api.trends_place(id=US_WOEID)
trends_querys = [x['query'] for x in response[0]['trends']]
trends_names = [x['name'] for x in response[0]['trends']]

with open('trends.txt', 'w') as stream:
	stream.write("\n".join(trends_names))

tweets = []
max_tweets = 200
for i, query in enumerate(trends_querys):
	print("Getting trend {0}/{1}".format(i+1, len(trends_querys)))
	tweets += [status.text for status in tweepy.Cursor(api.search, q=query, language='en').items(max_tweets)]

with open('tweets.txt', 'w') as stream:
	stream.write("\n".join(tweets))
