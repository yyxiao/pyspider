#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-22 10:15:31
# Project: boohee1
import re, requests, hashlib, time
from pyspider.libs.base_handler import *
import pymysql
import sys, json


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.boohee.com/food', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            # 不抓规则：1，非本站信息
            if not each.attr.href.startswith("http://www.boohee.com"):
                continue
            elif re.search("http://www.boohee.com/shiwu/.*", each.attr.href):
                self.crawl(each.attr.href, callback=self.detail_page)
            elif re.search("http://www.boohee.com/food/group/.*", each.attr.href):
                self.crawl(each.attr.href, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            'title' : response.doc('title').text(),
            'contents': response.doc('.margin10 > .content').text(),
            'content': {
                'name': response.doc('.margin10 > .content > dl .dt').text(),
                'value': response.doc('.margin10 > .content > dl .dd').text()
            }
        }
        result['title'] = response.doc('title').text()
        print response.doc('title').text()
        info = response.doc('.margin10 > .content').text()
        result['content'] = info
        return result

    # on_result 将数据存储于数据库
    def on_result(self, result):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        if not result or not result['title']:
            return
        # 连接配置信息
        mysql_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'root',
            'db': 'logdb',
            'charset': 'utf8',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        # 创建连接
        connection = pymysql.connect(**mysql_config)
        # 执行sql语句
        try:
            with connection.cursor() as cursor:
                # 执行sql语句，进行查询
                sql = 'insert boohee(url, title, contents, content) VALUES (%s, %s, %s, %s)'
                # 获取查询结果
                cursor.execute(sql, (str(result['url']), str(result['title']), str(result['contents']),
                                     json.dumps(result['content'], ensure_ascii=False)))
            # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
            connection.commit()
        finally:
            connection.close()
