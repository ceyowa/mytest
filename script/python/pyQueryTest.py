#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# By 陈有华
# Created on 2020-03-28 10:11:26

html = '''
<div id="container">
    <ul class="list">
         <li class="item-0">first item</li>
         <li class="item-1"><a href="link2.html">second item</a></li>
         <li class="item-0 active"><a href="link3.html"><span class="bold">third item</span></a></li>
         <li class="item-1 active"><a href="link4.html">fourth item</a></li>
         <li class="item-0"><a href="link5.html">fifth item</a></li>
     </ul>
 </div>
'''

from pyquery import PyQuery as pq
doc = pq(html)
items = doc('.list')#拿到items
# print(type(items))
# print(items)
lis = items.find('li')#利用find方法，查找items里面的li标签，得到的lis也可以继续调用find方法往下查找，层层剥离
# print(type(lis))
# print(lis)

# 也可以用.children()查找直接子元素
lis = items.children(':nth-child(1)')
print(type(lis))
print(lis)
print(lis.text())
# lis = items.children('.active')
# print(lis)