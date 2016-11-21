#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
"""
__author__ = xyy
__mtime__ = 2016/11/21
"""

'''
pyspider结果保存到数据库简单样例。
使用方法：
    1，把本文件放到pyspider/pyspider/database/mysql/目录下命名为mysqldb.py。
    2，修改本文件的数据库配置参数及建立相应的表和库。
    3，在脚本文件里使用from pyspider.database.mysql.mysqldb import SQL引用本代码.
    4，重写on_result方法，实例化sql并调用replace(replace方法参数第一个是表名，第二个是结果。)。简单例子如下：
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2015-01-26 13:12:04
# Project: jishubu.net

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
            print each.attr.href

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('HTML>BODY#presc>DIV.main>DIV.prices_box.wid980.clearfix>DIV.detail_box>DL.assort.tongyong>DD>A').text(),
        }
    def on_result(self, result):
        #print result
        if not result or not result['title']:
            return
        sql = SQL()
        sql.replace('info',**result)
'''
from six import itervalues
import mysql.connector


class SQL:
    username = 'root'  # 数据库用户名
    password = 'root'  # 数据库密码
    database = 'pyspider'  # 数据库
    host = 'localhost'  # 数据库主机地址
    connection = ''
    connect = True


placeholder = '%s'


def __init__(self):
    if self.connect:
        SQL.connect(self)


def escape(self, string):
    return '`%s`' % string


def connect(self):
    config = {
        'user': SQL.username,
        'password': SQL.password,
        'host': SQL.host
    }
    if SQL.database != None:
        config['database'] = SQL.database

    try:
        cnx = mysql.connector.connect(**config)
        SQL.connection = cnx
        return True
    except mysql.connector.Error as err:
        print("Something went wrong: ", err)
    return False


def replace(self, tablename=None, **values):
    if SQL.connection == '':
        print("Please connect first")
        return False

    tablename = self.escape(tablename)
    if values:
        _keys = ", ".join(self.escape(k) for k in values)
        _values = ", ".join([self.placeholder, ] * len(values))
        sql_query = "REPLACE INTO %s (%s) VALUES (%s)" % (tablename, _keys, _values)
    else:
        sql_query = "REPLACE INTO %s DEFAULT VALUES" % tablename

    cur = SQL.connection.cursor()
    try:
        if values:
            cur.execute(sql_query, list(itervalues(values)))
        else:
            cur.execute(sql_query)
        SQL.connection.commit()
        return True
    except mysql.connector.Error as err:
        print("An error occured: {}".format(err))
        return False