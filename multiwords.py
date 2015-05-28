import re
import collections
import csv
import subprocess

input_file = 'tweets_trends.txt'

p = subprocess.Popen(["../ark-tweet-nlp-0.3.2/runTagger.sh", "--no-confidence", "--output-format", "pretsv", "--quiet", input_file], stdout=subprocess.PIPE)
(output, err) = p.communicate()
token_list_temp = re.sub("\n", "\t", output.decode()).split("\t")

i=0
token_list=[]
while i<len(token_list_temp):
  token_list.append(token_list_temp[i:i+2])
  i+=3

dict_multiword = collections.defaultdict(int)

tweet1 = ''
for group in token_list:
    if len(group) == 2:
        tweet = group[0]
        tag = group[1]
    if tweet1 != tweet:
        words = tweet.split()
        tags = tag.split()

        word1 = ""
        word2 = ""
        tag1 = ""
        tag2 = ""
        pair = ""
        for i in range(0, len(words)-1):
            word = words[i]
            tag = tags[i]
            if tag == "N" or tag == "^":
                if tag1 in ["N", "^", "A", "V"]:
                    multiword = word1 + " " + word
                    dict_multiword[multiword]+=1
                if (tag1 in ["N", "^", "A"]) and (tag2 in ["N", "^", "A"]):
                    multiword = word2 + " " + word1 + " " + word
                    dict_multiword[multiword]+=1
                if (tag1 in ["P"]) and (tag2 in ["N", "^"]):
                    multiword = word2 + " " + word1 + " " + word
                    dict_multiword[multiword]+=1
            if tag == "V":
                if tag1 in ["N", "^", "R"]:
                    multiword = word1 + " " + word
                    dict_multiword[multiword]+=1
            word2 = word1
            tag2 = tag1
            word1 = word
            tag1 = tag
    tweet1 = tweet

ordered_dict_multiword = collections.OrderedDict(sorted(dict_multiword.items(), key=lambda t: t[1], reverse=True))
# print(ordered_dict_word.items())

w = csv.writer(open("dictionaryPair.csv", "w"))
for key, val in ordered_dict_multiword.items():
    if val > 1:
         w.writerow([key, val])
