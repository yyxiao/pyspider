# -*- coding:utf-8 -*-  
"""
Create on 16/11/29
Author xiaoyy
"""

from pyspider.libs.base_handler import *
import re


class Handler(BaseHandler):
    crawl_config = {
        "headers": {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/42.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Referer': 'http://www.xiumm.cc',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.xiumm.cc', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        #      for each in response.doc('a[href^="http"]').items():
        for i in range(51, 190):
            self.crawl("http://www.xiumm.cc/albums/page-{}.html".format(i), cookies=response.cookies,
                       callback=self.juti)

    @config(age=10 * 24 * 60 * 60)
    def juti(self, response):
        urllist = []
        url = re.findall(r'/photos/\w+-\d+\.html', response.text)
        #        print(response.text)
        for i in url:
            urllist.append("http://www.xiumm.cc{}".format(i))
        for depage in urllist:
            self.crawl(depage, cookies=response.cookies, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if each.attr.href.startswith("http://www.xiumm.cc/photos/") and each.attr.href.endswith("html"):
                self.crawl(each.attr.href, cookies=response.cookies, callback=self.detail_page)

        img_list = []
        img = re.findall(r'/data/\d+/\d\d/\d+\.jpg', response.text)
        #        print(response.text)
        for i in img:
            img_list.append("http://www.xiumm.cc{}".format(i))
        img_list = list(set(img_list))

        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "img": img_list,
        }