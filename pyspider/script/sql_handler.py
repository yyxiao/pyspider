#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
__author__ = xyy
__mtime__ = 2016/11/21
"""

from pyspider.libs.base_handler import *
from pyspider.database.mysql.mysqldb import SQL

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.jishubu.net/', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('p.pic a[href^="http"]').items():
            print(each.attr.href)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('HTML>BODY#presc>DIV.main>DIV.prices_box.wid980.clearfix>DIV.detail_box>DL.assort.tongyong>DD>A').text(),
        }

    def on_result(self, result):
        print(result)
        if not result or not result['title']:
            return
        sql = SQL()
        sql.replace('info', **result)