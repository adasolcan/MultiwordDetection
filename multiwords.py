import re
import collections
import csv
import subprocess

inputFile = 'tweets_1.txt'

p = subprocess.Popen(["../ark-tweet-nlp-0.3.2/runTagger.sh", "--no-confidence", "--output-format", "pretsv", "--quiet", inputFile], stdout=subprocess.PIPE)
(output, err) = p.communicate()
tokenList_temp = re.sub("\n", "\t", output).split("\t")

i=0
tokenList=[]
while i<len(tokenList_temp):
  tokenList.append(tokenList_temp[i:i+2])
  i+=3

print tokenList

words = ['']
dictWord = collections.defaultdict(int)
particles = collections.defaultdict(int)
f = open('prepositions.txt', 'r')
for prep in f:
    particles[prep.rstrip()]+=1
f.close()
f = open('articles.txt', 'r')
for article in f:
    particles[article.rstrip()]+=1
f.close()

tweet1 = ''
for group in tokenList:
    if len(group) == 2:
        tweet = group[0]
        tag = group[1]
    if tweet1 != tweet:
        words = tweet.split()
        tags = tag.split()
        print words
        print tags

        word1 = ""
        word2 = ""
        word3 = ""
        tag1 = ""
        tag2 = ""
        tag3 = ""
        pair = ""
        for i in range(0, len(words)-1):
            word = words[i]
            tag = tags[i]
            if word3!="" and word2!="" and word1!="" and word!="":
                if not((word1 in particles) or (word in particles)):
                    pair = word1 + " " + word
                    dictWord[pair]+=1
                if not(word2 in particles):
                     pair = word2 + " " + word1 + " " + word
                     dictWord[pair]+=1
                if not(word3 in particles):
                     pair = word1 + " " + word2 + " " + word3 + " " + word
                     dictWord[pair]+=1
            word1 = word
            tag1 = tag
            word2 = word1
            tag2 = tag1
            word3 = word2
            tag3 = tag2
    tweet1 = tweet

f.close()
# print(dictWord.items())

orderedDictWord = collections.OrderedDict(sorted(dictWord.items(), key=lambda t: t[1], reverse=True))
# print(orderedDictWord.items())

w = csv.writer(open("dictionaryPair.csv", "w"))
for key, val in orderedDictWord.items():
    if val > 1:
         w.writerow([key, val])
