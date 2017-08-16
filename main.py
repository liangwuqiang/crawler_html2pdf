# -*- coding:utf-8 -*-
import codecs
import csv
import jieba

import jieba.analyse
# import matplotlib.pyplot as plt
# import requests
# from scipy.misc import imread
# from wordcloud import WordCloud


def read_csv():
    with codecs.open('heart/weibo.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row['text']


def word_segment(texts):
    jieba.analyse.set_stop_words("heart/stopwords.txt")
    for text in texts:
        tags = jieba.analyse.extract_tags(text, topK=20)
        print(" ".join(tags))
        # break
        # yield " ".join(tags)

word_segment(read_csv())
