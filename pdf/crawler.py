# coding=utf-8
from __future__ import unicode_literals

import logging
import os
import re
import time

try:
    from urllib.parse import urlparse  # py3
except:
    # from urlparse import urlparse  # py2
    pass

import pdfkit
import requests
from bs4 import BeautifulSoup

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>

"""


class Crawler(object):
    """
    爬虫基类，所有爬虫都应该继承此类
    """
    name = None

    def __init__(self, name, start_url):
        """
        初始化
        :param name: 将要被保存为PDF的文件名称
        :param start_url: 爬虫入口URL
        """
        self.name = name
        self.start_url = start_url
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.start_url))

    @staticmethod
    def request(url, **kwargs):
        """
        网络请求,返回response对象
        :return:
        """
        response = requests.get(url, **kwargs)
        return response

    def parse_menu(self, response):
        """
        从response中解析出所有目录的URL链接
        """
        raise NotImplementedError

    def parse_body(self, response):
        """
        解析正文,由子类实现
        :param response: 爬虫返回的response对象
        :return: 返回经过处理的html正文文本
        """
        raise NotImplementedError

    def run(self):
        start = time.time()
        """用于pdf创建的参数"""
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'cookie': [
                ('cookie-name1', 'cookie-value1'),
                ('cookie-name2', 'cookie-value2'),
            ],
            'outline-depth': 10,
        }
        htmls = []
        """通过循环从菜单中逐个提取url,并取得每个url中的内容"""
        for index, url in enumerate(self.parse_menu(self.request(self.start_url))):
            html = self.parse_body(self.request(url))
            """构建文件名,将取得的html写入文件"""
            f_name = ".".join([str(index), "html"])
            with open(f_name, 'wb') as f:
                f.write(html)
            """使用文件名构建一个数组"""
            htmls.append(f_name)

        """生成pdf文件"""
        pdfkit.from_file(htmls, self.name + ".pdf", options=options)

        """删除临时的html文件"""
        for html in htmls:
            os.remove(html)
        """计算程序耗时"""
        total_time = time.time() - start
        print(u"总共耗时：%f 秒" % total_time)


class LiaoxuefengPythonCrawler(Crawler):
    """
    廖雪峰Python3教程
    """

    def parse_menu(self, response):
        """
        解析目录结构,获取所有URL目录列表
        :param response 爬虫返回的response对象
        :return: url生成器
        """
        soup = BeautifulSoup(response.content, "html.parser")
        """提取侧边栏的菜单目录"""
        menu_tag = soup.find_all(class_="uk-nav uk-nav-side")[1]
        for li in menu_tag.find_all("li"):
            url = li.a.get("href")
            """处理链接中没有http的情况,即原来使用的是相对路径"""
            if not url.startswith("http"):
                url = "".join([self.domain, url])  # 补全为全路径
            """让函数直接返回迭代结果"""
            yield url

    def parse_body(self, response):
        """
        解析正文
        :param response: 爬虫返回的response对象
        :return: 返回处理后的html文本
        """
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            """提取内容"""
            body = soup.find_all(class_="x-wiki-content")[0]
            """对获取的内容进行重构(重新排列)"""
            # 加入标题, 居中显示
            title = soup.find('h4').get_text()
            center_tag = soup.new_tag("center")
            title_tag = soup.new_tag('h1')
            title_tag.string = title
            center_tag.insert(1, title_tag)
            body.insert(1, center_tag)

            html = str(body)

            """图片url改用绝对地址"""
            # body中的img标签的src相对路径的改成绝对路径
            pattern = "(<img .*?src=\")(.*?)(\")"

            def func(m):
                if not m.group(2).startswith("http"):
                    rtn = "".join([m.group(1), self.domain, m.group(2), m.group(3)])
                    return rtn
                else:
                    return "".join([m.group(1), m.group(2), m.group(3)])
            """替换html中图片的超链接"""
            html = re.compile(pattern).sub(func, html)
            """用模板,产生完整的html,编码后返回"""
            html = html_template.format(content=html)
            html = html.encode("utf-8")  # 为什么不直接在soup中解码呢?
            return html
        except Exception as e:
            print(e)
            logging.error("解析错误", exc_info=True)


if __name__ == '__main__':
    start_url = "http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000"
    crawler = LiaoxuefengPythonCrawler("廖雪峰Git", start_url)
    crawler.run()
