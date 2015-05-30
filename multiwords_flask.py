from flask import Flask
from flask import render_template

import tweepy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/trends')
def get_trends():
	keys = []
	with open('keys.txt') as stream:
	    keys = [line.strip() for line in stream]
	[consumer_key, consumer_secret, access_token, access_token_secret] = keys


	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	US_WOEID = '23424977'

	response = api.trends_place(id=US_WOEID)
	trends_names = [x['name'] for x in response[0]['trends']]
	return render_template('trends.html', trends = trends_names)

if __name__ == '__main__':
	app.debug = True
	app.run()