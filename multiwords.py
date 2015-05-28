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
dict_word = collections.defaultdict(int)

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
            word = words[i].lower()
            tag = tags[i]

            if tag in ["N", "A", "V", "R", "P"]:
                dict_word[word] += 1

            if tag == "N":
                if tag1 in ["N", "A", "V"]:
                    multiword = word1 + " " + word
                    dict_multiword[multiword] += 3
                if (tag1 in ["N", "A"]) and (tag2 in ["N", "A"]):
                    multiword = word2 + " " + word1 + " " + word
                    dict_multiword[multiword] += 4
                if (tag1 in ["P"]) and (tag2 in ["N"]):
                    multiword = word2 + " " + word1 + " " + word
                    dict_multiword[multiword] += 4
            if tag == "V":
                if tag1 in ["N", "R"]:
                    multiword = word1 + " " + word
                    dict_multiword[multiword] += 3
            word2 = word1
            tag2 = tag1
            word1 = word
            tag1 = tag
    tweet1 = tweet

dict_multiword_score = collections.defaultdict(int)

for key, val in dict_multiword.items():
    dict_multiword_score[key] = val
    words = key.split()
    for word in words:
        dict_multiword_score[key] -= dict_word[word]


ordered_dict_multiword = collections.OrderedDict(sorted(dict_multiword.items(), key=lambda t: t[1], reverse=True))
ordered_dict_word = collections.OrderedDict(sorted(dict_word.items(), key=lambda t: t[1], reverse=True))
ordered_dict_multiword_score = collections.OrderedDict(sorted(dict_multiword_score.items(), key=lambda t: t[1], reverse=True))

w = csv.writer(open("dictionaryMultiword.csv", "w"))
for key, val in ordered_dict_multiword_score.items():
    if val > 1:
        w.writerow([key, val])


w = csv.writer(open("dictionaryWord.csv", "w"))
for key, val in ordered_dict_word.items():
    if val > 1:
         w.writerow([key, val])
