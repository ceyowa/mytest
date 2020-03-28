#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-03-28 10:11:26
# Project: CountryCodeJson

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.51zzl.com/rcsh/gjqh.asp', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        print(response.doc('table'))
        result = []
        for each in response.doc('#content tr').items():
            if each.attr.bgcolor == '#cccccc':
                continue
            result.append({
                'enName': each.children(':nth-child(1)').text(),
                'cnName': each.children(':nth-child(2)').text(),
                'code': each.children(':nth-child(4)').text(),
            })

        return result
