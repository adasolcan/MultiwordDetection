import re
import collections
import csv
import subprocess
import json

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

multiword_patterns = [["N", "N"], ["A", "S"], ["V", "N"], 
                    ["N", "N", "N"], ["A", "N", "N"], ["N", "A", "N"], ["A", "A", "N"], ["N", "P", "N"], 
                    ["N", "V"], ["R" , "V"], ["N", "P", "A", "N"], ["N", "P", "N", "N"],
                    ["A", "N", "P", "N", "N", "N", "P", "N"]]

tweet1 = ''
words_total = 0
for group in token_list:
    if len(group) == 2:
        tweet = group[0]
        tag = group[1]
    if tweet1 != tweet:
        words = tweet.split()
        tags = tag.split()
        word1 = ""
        word2 = ""
        word3 = ""
        tag1 = ""
        tag2 = ""
        tag3 = ""
        pair = ""
        for i in range(0, len(words)-1):
            word = words[i].lower()
            tag = tags[i]

            if tag in ["N", "A", "V", "R", "P"]:
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
    tweet1 = tweet

dict_multiword_score = collections.defaultdict(int)

for key, val in dict_multiword.items():
    words = key.split()
    dict_multiword_score[key] = val * (len(words) + 1)
    for word in words:
        dict_multiword_score[key] -= dict_word[word]

ordered_dict_multiword_score = collections.OrderedDict(sorted(dict_multiword_score.items(), key=lambda t: t[1], reverse=True))

with open("dictionaryMultiword.json", "w") as outfile:
    json_data = []
    for key, val in ordered_dict_multiword_score.items():
        words = key.split()
        json_obj = {'multiword':key, 'score':val, 'no_app':dict_multiword[key]}
        for word in words:
            json_obj[word+" no_app"] = dict_word[word] - dict_multiword[key]
        json_data.append(json_obj)
    json.dump(json_data, outfile, indent=4)