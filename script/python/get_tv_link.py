#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2020-03-29 16:59:05
import requests
# 引入Beautiful Soup包
# from bs4 import BeautifulSoup
from pyquery import PyQuery

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

r = requests.get('https://www.meijubie.com/movie/index32718.html', headers = headers)
# print(r.text)
# soup = BeautifulSoup(r.text, 'lxml')
# links = soup.findAll("#downlist1 .ldgcopy")
doc = PyQuery(r.text)
# print(doc)
links = doc('#downlist1 script').text().split(';')[0].split('=')[1].strip().replace('"', '').split('###')
results = []
for item in links:
    results.append(item.split('$')[1])
print(results)
