import re
import collections
import subprocess
import json

from langdetect import detect

input_file = 'tweets_trends2June.txt'

p = subprocess.Popen(["../ark-tweet-nlp-0.3.2/runTagger.sh", "--no-confidence", "--input-format", "text", "--output-format", "pretsv", "--quiet", input_file], stdout=subprocess.PIPE)
(output, err) = p.communicate()
token_list_temp = re.sub("\n", "\t", output.decode()).split("\t")

i=0
token_list=[]
while i<len(token_list_temp):
	token_list.append(token_list_temp[i:i+2])
	i+=3

multiword_patterns = [["N", "V"], ["^", "^"], ["N", "^"], ["^", "N"], ["N", "N"],
					["A", "N"], ["A", "^"], ["V", "N"], ["V", "^"], ["V", "T"],
					["N", "V"], ["^", "V"], ["R" , "V"],
					["V", "T", "T"], ["V", "T", "P"],
					["N", "O", "N"], ["^", "O", "N"], ["N", "O", "^"], ["^", "O", "^"],
					["D", "D", "N"], ["D", "D", "^"], ["V", "D", "N"], ["V", "D", "^"], ["V", "T", "P"],
					["N", "N", "N"], ["N", "N", "^"], ["N", "^", "N"], ["^", "N", "N"], ["N", "^", "^"], ["^", "N", "^"], ["^", "^", "N"], ["^", "^", "^"],
					["A", "N", "N"], ["A", "N", "^"], ["A", "^", "N"], ["A", "^", "^"],
					["N", "A", "N"], ["^", "A", "^"], ["N", "A","^"], ["^", "A", "N"],
					["A", "A", "N"], ["A", "A", "^"],
					["N", "P", "N"], ["^", "P", "N"], ["N", "P", "^"], ["^", "P", "^"],
					["N", "P", "A", "N"], ["^", "P", "A", "N"], ["N", "P", "A", "^"], ["^", "P", "A", "^"],
					["N", "P", "D", "N"], ["^", "P", "D", "N"], ["N", "P", "D", "^"], ["^", "P", "D", "^"],
					["N", "P", "N", "N"], ["^", "P", "N", "N"], ["N", "P", "^", "N"], ["N", "P", "N", "^"], ["N", "P", "^", "^"], ["^", "P", "N", "^"], ["^", "P", "^", "N"], ["^", "P", "^", "^"],
					["N", "N", "P", "N"], ["N", "N", "P", "^"], ["N", "^", "P", "N"], ["^", "N", "P", "N"], ["^", "^", "P", "N"], ["^", "N", "P", "^"], ["N", "^", "P", "^"], ["^", "^", "P", "^"]]

dict_multiword = collections.defaultdict(int)
dict_word = collections.defaultdict(int)

tweet1 = ''
words_total = 0
for group in token_list:
	tweet = ''
	if len(group) == 2:
		tweet = group[0].lower()
		tag = group[1]
		lang = ''
		try:
			lang = detect(tweet)
		except: 
			pass
	if (tweet1 != tweet) and (lang == 'en'):
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
			word = words[i]
			tag = tags[i]

			if tag in ["N", "^", "A", "V", "R"]:
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
	dict_multiword_score[key] = val
	for word in words:
		if word in dict_word:
			dict_multiword_score[key] -= dict_word[word] - val

ordered_dict_multiword_score = collections.OrderedDict(sorted(dict_multiword_score.items(), key=lambda t: t[1], reverse=True))

with open("dictionaryMultiword.json", "w") as outfile:
	json_data = []
	for key, val in ordered_dict_multiword_score.items():
		if val>10: 
			words = key.split()
			json_obj = {'multiword':key, 'score':val, 'no_app':dict_multiword[key]}
			for word in words:
				if word in dict_word:
					json_obj[word+" no_app"] = dict_word[word] - dict_multiword[key]
			json_data.append(json_obj)
	json.dump(json_data, outfile, indent=4)