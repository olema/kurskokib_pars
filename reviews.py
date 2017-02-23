#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Выборка сообщений на модерации со страницы отзывов на сайте
# http://kurskokib.ru
# Имена переменных в тэгах <TD>:
#   name="var0" - имя пользователя, оставившего сообщение;
#   name="var1" - адрес сайта;
#   name="var2" - e-mail;
#   name="var3" - текст отзыва;
#   name="var4" - ip-address с которого зашел пользователь;
#   name="var5" - UNIX-timestamp;
#   name="var6" - браузер;
#   name="var7" - ""

import requests
import sys
import configparser

# TODO - работа с конфигом reviews.config
# с помощью модуля configparser
config = configparser.ConfigParser()
config.read('reviews.config')
print(config.sections())
urls = config['urls']
url_admin = urls['url_admin']
url_rev = urls['url_rev']
print(url_admin, url_rev)

# Читаем страницу с сайта
s = requests.session()
data = {"ln": sys.argv[1], "pd": sys.argv[2]}
r = s.post(url_admin, data=data)
r = s.get(url_rev)
print(r.url)

# Оставляем только строки, с отзывами "на модерации"
l = ''
moder = []
in_moder_block = False
for l in r.text.splitlines():
    if 'Отзывы на модерации' in l:
        in_moder_block = True
    if 'Отзывы в базе' in l:
        in_moder_block = False
    if in_moder_block:
        moder.append(l.strip())

# Формируем список messages с словарями полей var0..var7
messages = []
d = dict()
for l in moder:
    if 'name="var0"' in l:
        fv = l.find('value=')
        vval = l[fv:fv+30]
        d['var0'] = vval
    if 'name="var1"' in l:
        fv = l.find('value=')
        vval = l[fv:fv+30]
        d['var1'] = vval
    if 'name="var2"' in l:
        fv = l.find('value=')
        vval = l[fv:fv+30]
        d['var2'] = vval
        messages.append(d)
        d = dict()

for d in messages:
    for item in d:
        print(item, ': ', d[item])

