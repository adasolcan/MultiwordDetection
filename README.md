Computational approach of multi word detection using tweets

In order to run the app you need to follow this steps: <br />
1. git clone git@github.com:adasolcan/MultiwordDetection.git <br />
2. wget https://ark-tweet-nlp.googlecode.com/files/ark-tweet-nlp-0.3.2.tgz <br />
3. tar -xvzf ark-tweet-nlp-0.3.2.tgz <br />
4. cd MultiwordDetection <br />
5. pip3 install -r requirements.txt <br />
6. register a Twitter app: https://apps.twitter.com/ <br />
7. create a file named keys.txt which contains on separate lines the consumer keys(consumer key, consumer secret) and the access tokens (access token, access token secret) of the Twitter app <br />
8. python3 multiwords_flask.py <br />
9. In your browser go to http://127.0.0.1:5000/ <br />
