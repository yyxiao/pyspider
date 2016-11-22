#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-10-27 16:32:42
# Project: gsjb
from pyspider.libs.base_handler import *
import re, requests, hashlib, time


class Handler(BaseHandler):
    crawl_config = {

    }
    app_config = {
        'appid': 2393347,
        'appname': 'gsjb'
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.gsjb.com/Index.html', callback=self.index_page)

    @config(age=24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            # 不抓规则：1，非本站新闻， 2，记者之窗
            if not each.attr.href.startswith("http://www.gsjb.com/news") or \
                    each.attr.href.startswith("http://www.gsjb.com/news/jzzc"):
                continue
            elif re.search("http://www.gsjb.com/news/.*?/\d*\.htm[l]?", each.attr.href):
                self.crawl(each.attr.href, callback=self.detail_page)
            else:
                self.crawl(each.attr.href, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        result = {
            'url': response.url,
            'itemid': self.get_md5(response.url),
            'appid': self.app_config['appid'],
            'appname': self.app_config['appname']}
        # cate id
        p = self.get_position(response.doc('.STYLE2 > a').text())
        if p: result['cateid'] = p

        result['title'] = response.doc('title').text()
        c1 = response.doc('.STYLE5 > div').text()
        c2 = response.doc('.nph_intro > div').text()
        c3 = response.doc('#MyContent > #MyContent > p').text()
        result['content'] = c1 or c2 or c3
        # 时间
        tstr2 = response.doc('td > .STYLE4').text()
        tstr1 = response.doc('.del').text()
        t = self.get_timestamp(tstr2 or tstr1)
        if t: result['item_modify_time'] = t

        # 图片列表
        pic_list = [x.attr.src for x in list(response.doc('img').items())[0:4]]
        if pic_list: result['pic_list'] = pic_list
        return result

    # def on_result(self, result):
    #    requests.post("http://www.kely.live:8080", result)

    def get_md5(self, s):
        m = hashlib.md5()
        m.update(s)
        return m.hexdigest()

    def get_timestamp(self, s):
        try:
            if not s: return 0
            date = re.findall(ur"(\d{4})[年|/]*?(\d{1,2})[月|/]*?(\d{1,2})[日|/]*?", s)
            date = "-".join(date[0] if date else [])
            dtime = re.findall(ur"(\d{1,2}:\d{1,2}:\d{1,2})", s)
            dtime = dtime[0] if dtime else ""
            if date and not dtime:
                t_obj = time.strptime("{d} {t}".format(d=date, t=dtime).strip(), "%Y-%m-%d")
                return int(time.mktime(t_obj))
            elif date and dtime:
                t_obj = time.strptime("{d} {t}".format(d=date, t=dtime).strip(), "%Y-%m-%d %H:%M:%S")
                return int(time.mktime(t_obj))
            else:
                return 0
        except Exception as e:
            return 0

    def get_position(self, p):
        if not p:
            return None
        return p.split(" ")[-1] if p.split(" ") else ""