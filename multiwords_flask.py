import tweepy
import re
import collections
import subprocess
import json

from flask import Flask, render_template, request
from langdetect import detect

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './'


def get_twitter_api():
    keys = []
    with open('keys.txt') as stream:
        keys = [line.strip() for line in stream]
    [consumer_key, consumer_secret, access_token, access_token_secret] = keys

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/trends')
def get_trends():
    api = get_twitter_api()
    US_WOEID = '23424977'

    response = api.trends_place(id=US_WOEID)
    trends_names = [x['name'] for x in response[0]['trends']]
    return json.dumps(trends_names)


@app.route('/search_trends', methods=['GET', 'POST'])
def search_trends():
    tweets = []
    if request.files.get('file'):
        tweets = [x.decode().strip()
                  for x in request.files['file'].stream.readlines()]
        tweets_file = 'tweets_upload.txt'
    else:
        tweets_file = 'tweets_trends.txt'
        api = get_twitter_api()
        trends_querys = json.loads(request.form['data'])

        tweets = []
        max_tweets = 20
        try:
            for i, query in enumerate(trends_querys):
                print("Getting trend {0}/{1}".format(i+1, len(trends_querys)))
                tweets += [status.text for status in
                           tweepy.Cursor(api.search, language='en',
                                         q=query, ).items(max_tweets)]
        except:
            tweets = None

    if tweets:
        with open(tweets_file, 'w') as stream:
            stream.write("\n".join(tweets))

    p = subprocess.Popen(["../ark-tweet-nlp-0.3.2/runTagger.sh",
                          "--no-confidence", "--input-format", "text",
                          "--output-format", "pretsv", "--quiet", tweets_file],
                         stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    token_list_temp = re.sub("\n", "\t", output.decode()).split("\t")

    i = 0
    token_list = []
    while i < len(token_list_temp):
        token_list.append(token_list_temp[i:i+2])
        i += 3

    multiword_patterns = [
        ["^", "^"], ["N", "^"], ["^", "N"], ["N", "N"], ["A", "N"],
        ["A", "^"], ["V", "N"], ["V", "^"], ["V", "T"], ["R", "V"],
        ["V", "T", "T"], ["V", "T", "P"], ["V", "D", "N"], ["V", "D", "^"],
        ["N", "O", "N"], ["^", "O", "N"], ["N", "O", "^"], ["^", "O", "^"],
        ["D", "D", "N"], ["D", "D", "^"], ["V", "D", "N"], ["V", "D", "^"],
        ["V", "T", "P"], ["N", "N", "N"], ["N", "N", "^"], ["N", "^", "N"],
        ["^", "N", "N"], ["N", "^", "^"], ["^", "N", "^"], ["^", "^", "N"],
        ["^", "^", "^"], ["A", "N", "N"], ["A", "N", "^"], ["A", "^", "N"],
        ["A", "^", "^"], ["N", "A", "N"], ["^", "A", "^"], ["N", "A", "^"],
        ["^", "A", "N"], ["A", "A", "N"], ["A", "A", "^"], ["N", "P", "N"],
        ["^", "P", "N"], ["N", "P", "^"], ["^", "P", "^"],
        ["N", "P", "A", "N"], ["^", "P", "A", "N"], ["N", "P", "A", "^"],
        ["^", "P", "A", "^"], ["N", "P", "D", "N"], ["^", "P", "D", "N"],
        ["N", "P", "D", "^"], ["^", "P", "D", "^"], ["N", "P", "N", "N"],
        ["^", "P", "N", "N"], ["N", "P", "^", "N"], ["N", "P", "N", "^"],
        ["N", "P", "^", "^"], ["^", "P", "N", "^"], ["^", "P", "^", "N"],
        ["^", "P", "^", "^"], ["N", "N", "P", "N"], ["N", "N", "P", "^"],
        ["N", "^", "P", "N"], ["^", "N", "P", "N"], ["^", "^", "P", "N"],
        ["^", "N", "P", "^"], ["N", "^", "P", "^"], ["^", "^", "P", "^"]]

    dict_multiword = collections.defaultdict(int)
    dict_word = collections.defaultdict(int)

    last_tweet = ''
    words_total = 0
    for group in token_list:
        if len(group) == 2:
            [tweet, tag] = group

        if last_tweet != tweet:
            words = tweet.split()
            tags = tag.split()
            word1 = ""
            word2 = ""
            word3 = ""
            tag1 = ""
            tag2 = ""
            tag3 = ""
            pair = ""

            for i in range(len(words)):
                word = words[i].lower()
                tag = tags[i]

                if tag in ["N", "A", "V", "R", "P", "O"]:
                    dict_word[word] += 1
                    words_total += 1

                if [tag1, tag] in multiword_patterns:
                    multiword = word1 + " " + word
                    dict_multiword[multiword] += 1

                if [tag2, tag1, tag] in multiword_patterns:
                    multiword = word2 + " " + word1 + " " + word
                    dict_multiword[multiword] += 1

                if [tag3, tag2, tag1, tag] in multiword_patterns:
                    multiword = word3 + " " + word2 + " " + word1 + " " + word
                    dict_multiword[multiword] += 1

                word3 = word2
                tag3 = tag2
                word2 = word1
                tag2 = tag1
                word1 = word
                tag1 = tag
        last_tweet = tweet

    dict_multiword_score = collections.defaultdict(int)
    for key, val in dict_multiword.items():
        words = key.split()
        score = val

        for word in words:
            if word in dict_word:
                score -= dict_word[word] - val

            if score > 0:
                lang = ''

                try:
                    lang = detect(key)
                except:
                    pass

                if lang == 'en':
                    dict_multiword_score[key] = score

    ordered_dict_multiword_score = collections.OrderedDict(
        sorted(dict_multiword_score.items(), key=lambda t: t[1], reverse=True))
    return json.dumps(ordered_dict_multiword_score)

if __name__ == '__main__':
    app.debug = True
    app.run()
