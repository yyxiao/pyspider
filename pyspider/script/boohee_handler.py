#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-22 10:15:31
# Project: pyspider
import re, requests, hashlib, time
from pyspider.libs.base_handler import *
import pymysql
import sys, json


class Handler(BaseHandler):
    crawl_config = {
    }

    search_list = ['青刀豆', '土豆', '冬瓜']
    not_search_type = ['家常菜', '上海菜', '北京菜', '私家菜', '清真菜']

    @every(minutes=24 * 60)
    def on_start(self):
        # self.crawl('http://www.boohee.com/food', callback=self.index_page)
        for i in range(len(self.search_list)):
            self.crawl('http://www.boohee.com/food/search?keyword=' + str(self.search_list[i]),
                       callback=self.index_page,
                       # 传递参数
                       save=self.search_list[i])

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            # 不抓规则：1，非本站信息
            if not each.attr.href.startswith("http://www.boohee.com"):
                continue
            elif each.attr.href.startswith("http://www.boohee.com/food/view_menu"):
                continue
            elif re.search("http://www.boohee.com/shiwu/.*", each.attr.href):
                self.crawl(each.attr.href, callback=self.detail_page, save=response.save)
            elif re.search("http://www.boohee.com/food/group/.*", each.attr.href):
                self.crawl(each.attr.href, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        other_all = response.doc('.basic-infor > li').text().split('红绿灯')[0].strip().split(' ')
        name = response.doc('.crumb').text().split('/')[-1].strip()
        search_title = '别名：'
        other_name = ''
        if search_title in other_all:
            for i in range(len(other_all)):
                if search_title == other_all[i]:
                    other_name = other_all[i + 1]
                    other_name_list = other_name.split('、')
                    if response.save in other_name_list:
                        name = response.save
        else:
            other_name = ''
        # 处理分类数据（炒菜过滤）
        type = response.doc('.crumb').text().split('/')[-2].strip()
        if type not in self.not_search_type:
            result = {
                "url": response.url,
                'name': name,
                'type': type,
                'contents': response.doc('.margin10 > .content').text().split('>>')[0].strip(),
                'other_name': other_name
            }
        else:
            result = None
        return result


        # on_result 将数据存储于数据库
        # def on_result(self, result):
        #     reload(sys)
        #     sys.setdefaultencoding('utf-8')
        #     if not result or not result['title']:
        #         return
        #     # 连接配置信息
        #     mysql_config = {
        #         'host': '127.0.0.1',
        #         'port': 3306,
        #         'user': 'root',
        #         'password': 'root',
        #         'db': 'logdb',
        #         'charset': 'utf8',
        #         'cursorclass': pymysql.cursors.DictCursor,
        #     }
        #     # 创建连接
        #     connection = pymysql.connect(**mysql_config)
        #     # 执行sql语句
        #     try:
        #         with connection.cursor() as cursor:
        #             # 执行sql语句，进行查询
        #             sql = 'insert boohee(url, title, contents, content) VALUES (%s, %s, %s, %s)'
        #             # 获取查询结果
        #             cursor.execute(sql, (str(result['url']), str(result['title']), str(result['contents']),
        #                                  json.dumps(result['content'], ensure_ascii=False)))
        #         # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        #         connection.commit()
        #     finally:
        #         connection.close()
