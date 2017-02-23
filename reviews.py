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


def config(confname):
   # Работа с конфигом reviews.config с помощью модуля configparser.
   # Возвращает словарь с переменными из конфига confname
   # TODO Добавить проверку существования файла из confname.

    config = configparser.ConfigParser()
    config.read(confname)
    dict_var = dict()
    try:
        urls = config['urls']
        dict_var['url_admin'] = urls['url_admin']
        dict_var['url_rev'] = urls['url_rev']
    except KeyError:
        # TODO Добавить выдачу ошибки в файл-флаг и на email
        print('Error...')
        exit(-1)
    return dict_var


def tagparse(seekstring, namevar):
    # Ищет в строке seekstring имя namevar вида name="var0" и возвращает строку,
    # которая содержится в valuevar="xxxx" между кавычками (без кавычек).
    # Если namevar не найдена - возвращает пустую строку?
    #   пример: seekstring = '<TD name="var1" value="Иванов"'
    #           namevar = 'var1'
    #           Функция должна вернуть 'Иванов'
    if namevar not in seekstring:
        return ''
    else:
        return 'YEAH!!!!!'


def main():
    # Читаем переменные из файла конфигурации
    dvar = config('reviews.config')

    # Читаем страницу с сайта
    s = requests.session()
    data = {"ln": sys.argv[1], "pd": sys.argv[2]}
    r = s.post(dvar['url_admin'], data=data)
    r = s.get(dvar['url_rev'])
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
            break
        if in_moder_block:
            moder.append(l.strip())

    # DEBUG Для отладки
    f = open('moder_block.txt', 'w')
    for l in moder:
        f.write(l + '\n')
    f.close()

    # В moder[] - строки из блока "на модерации"
    print('\n\n****** test function tagparse() *********')
    print('moder[1] = ', moder[1])
    print('tagparse(moder[1], "name") = ', tagparse(moder[1], 'name'))
    print('****** test function tagparse() *********\n\n')

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

if __name__ == '__main__':
    main()
