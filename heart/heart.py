# -*- coding:utf-8 -*-
import codecs
import csv
import re

import jieba.analyse
import matplotlib.pyplot as plt
import requests
from scipy.misc import imread
from wordcloud import WordCloud

__author__ = 'liuzhijun'

"""一个字典"""
cookies = {
    "ALF": "xxxx",
    "SCF": "xxxxxx.",
    "SUBP": "xxxxx",
    "SUB": "xxxx",
    "SUHB": "xxx-", "xx": "xx", "_T_WM": "xxx",
    "gsScrollPos": "", "H5_INDEX": "0_my", "H5_INDEX_TITLE": "xxx",
    "M_WEIBOCN_PARAMS": "xxxx"
}


def fetch_weibo():
    """从weibo中获取数据"""
    api = "http://m.weibo.cn/index/my?format=cards&page=%s"
    for i in range(1, 102):
        response = requests.get(url=api % i, cookies=cookies)
        data = response.json()[0]
        groups = data.get("card_group") or []
        for group in groups:
            text = group.get("mblog").get("text")
            text = text.encode("utf-8")

            def cleanring(content):
                """
                去掉无用字符
                """
                pattern = "<a .*?/a>|<i .*?/i>|转发微博|//:|Repost|，|？|。|、|分享图片"
                content = re.sub(pattern, "", content)
                return content

            text = cleanring(text).strip()
            if text:
                yield text


def write_csv(texts):
    """将数据写入csv中,包含字段名,以表格的形式,以逗号分割,相当于数据库的表"""
    with codecs.open('./weibo.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["text"])
        writer.writeheader()
        for text in texts:
            writer.writerow({"text": text})


def read_csv():
    """从文件中读取数据"""
    with codecs.open('./weibo.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row['text']


def word_segment(texts):
    """通过jieba来抽取词组"""
    jieba.analyse.set_stop_words("./stopwords.txt")
    for text in texts:
        tags = jieba.analyse.extract_tags(text, topK=20)
        yield " ".join(tags)


def generate_img(texts):
    """由词组来生成图像"""
    data = " ".join(text for text in texts)

    # print(data)
    mask_img = imread('./heart-mask.jpg', flatten=True)

    """这里需要安装wordcloud,我的安装没通过,没法进行测试"""
    wordcloud = WordCloud(
        font_path='msyh.ttc',
        background_color='white',
        mask=mask_img
    ).generate(data)
    # plt.imshow(wordcloud)
    # plt.axis('off')
    # plt.savefig('./heart.jpg', dpi=600)


def p(text):
    print(text)
    print(type(text))

if __name__ == '__main__':
    # texts = fetch_weibo()  # 取数据
    # write_csv(texts)  # 写数据
    # generate_img(word_segment(read_csv()))  # 读数据,解析数据,数据绘图
    content = read_csv()
    words = word_segment(content)
    generate_img(words)
    # for item in words:
    #     p(item)
    # pass
