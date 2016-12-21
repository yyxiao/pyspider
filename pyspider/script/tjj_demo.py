# -*- coding:utf-8 -*-  
"""
Create on 16/12/21
Author xiaoyy
"""

from pyspider.libs.base_handler import *

# 国家统计局2015年统计用区划代码和城乡划分代码
class Handler(BaseHandler):
    crawl_config = {
        'retries': 30,
    }
    # retry_delay = {
    #     0: 30,
    #     1: 5 * 60,
    #     2: 10 * 60,
    #     3: 30 * 60,
    #     '': 30 * 60
    # }

    @every(minutes=2 * 24 * 60)
    def on_start(self):
        self.crawl('http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2015/index.html', callback=self.index_page)

    @config(age=2 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            self.crawl(each.attr.href, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            self.crawl(each.attr.href, callback=self.detail_country)
        ret = []
        for tr in response.doc('.citytr').items('tr'):
            lis = [i.text() for i in tr.items('a')]
            lis[0] = int(lis[0])
            ret.append({'_id': int(lis[0]), 'name': lis[1]})

        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "data": ret
        }

    @config(priority=2)
    def detail_country(self, response):
        for each in response.doc('a[href^="http"]').items():
            self.crawl(each.attr.href, callback=self.detail_towntr)
        ret = []
        for tr in response.doc('.countytr').items('tr'):
            lis = [i.text() for i in tr.items('a')]
            ret.append({'_id': int(lis[0]), 'name': lis[1]})

        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "data": ret
        }

    @config(priority=2)
    def detail_towntr(self, response):
        for each in response.doc('a[href^="http"]').items():
            self.crawl(each.attr.href, callback=self.detail_villagetr)
        ret = []
        for tr in response.doc('.towntr').items('tr'):
            lis = [i.text() for i in tr.items('a')]
            ret.append({'_id': int(lis[0]), 'name': lis[1]})

        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "data": ret
        }

    @config(priority=2)
    def detail_villagetr(self, response):
        ret = []
        for tr in response.doc('.villagetr').items('tr'):
            lis = [i.text() for i in tr.items('td')]
            ret.append({'_id': int(lis[0]), 'name': lis[2], 'type': lis[1]})

        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "data": ret
        }