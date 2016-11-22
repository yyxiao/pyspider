# -*- coding:utf-8 -*-  
"""
Create on 16/11/22
Author xiaoyy
"""

import pymysql
import sys, json

def search_blob_demo():
    # 连接配置信息
    mysql_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'db': 'resultdb',
        'charset': 'utf8',
        'cursorclass': pymysql.cursors.DictCursor,
    }
    # 创建连接
    connection = pymysql.connect(**mysql_config)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，进行查询
            sql = 'select * from boohee'
            # 获取查询结果
            cursor.execute(sql)
            cursor.fetchone()
            data = cursor.fetchone();
            print(data)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    finally:
        connection.close()