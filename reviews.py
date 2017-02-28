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
import logging


def log_init():
    ''' Функция инциализации подсистемы логирования

    '''
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                        level=logging.DEBUG,
                        filename=u'reviews.log')
    return True


def check_cmd():
    '''
        Проверка параметров коммандной строки
    '''
    if len(sys.argv) < 3:
        print('\nИспользование: ./reviews.py login password [-f]')
        print('    где:')
        print('       - login -  логин от страницы администратора;')
        print('       - password -  пароль от страницы администратора;')
        print('       - -f  - сформировать файл timestamps.\n')
        return False
    else:
        return True


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
    # Пока рассчитана на возврат value из var5 (timestamp)
    #
    # Ищет в строке seekstring имя namevar вида name="var0" и возвращает строку,
    # которая содержится в valuevar="xxxx" между кавычками (без кавычек).
    # Если namevar не найдена - возвращает пустую строку?
    #   пример: seekstring = '<TD name="var1" value="Иванов"'
    #           namevar = 'var1'
    #           Функция должна вернуть 'Иванов'
    if namevar not in seekstring:
        return ''
    else:
        valpos = seekstring.find('value="')
        tmpstr = seekstring[valpos+7:valpos+17]
        return tmpstr

# main
def main():
    # Проверяем параметры коммандной строки
    if not check_cmd():
        exit(-1)

    # TODO Инициализация подсистемы логирования
    if not log_init():
        exit(-1)

    logging.info(u'Start testing reviews {}.'.format(sys.platform))

    # TODO Проверка доступности сети

    # TODO Проверка доступности сайта kurskokib.ru

    #
    # Читаем переменные из файла конфигурации
    # dvar - словарь
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

    # DEBUG moder[] - строки из блока "на модерации"
    print('\n\n****** test function tagparse() *********')
    for l in moder:
        respars = tagparse(l, 'var5')
        if respars != '':
            print(respars)
    print('****** test function tagparse() *********\n\n')

    # Сформируем список таймстампов текущекго состояния
    real_timestamps = []
    for l in moder:
        respars = tagparse(l, 'var5')
        if respars != '':
            real_timestamps.append(respars)
    print(real_timestamps)

    # Если в командной строке задан параметр -f
    f_param = False
    for i in sys.argv:
        if '-f' in i:
            f_param = True
    if f_param:
        f = open('timestamps', 'w')
        for l in real_timestamps:
            f.write(l+'\n')
        f.close()

    # Открываем ранее сохраненные timestamp
    tss = []
    for line in open('timestamps', 'r'):
        tss.append(line.strip())

    print('На предыдущей модерации ' + str(len(tss)) + ' отзывов')
    print(tss)

    # Проверяем новые отзывы
    #   tss - список со старыми
    #   real_timestamps - новый список
    print('\nСравниваем кол-во элементов..."')
    if len(tss) != len(real_timestamps):
        print('---> НЕ РАВНЫ! ')
    # если равны - сверяем по элементам
    else:
        print('---> Равны...')
        print('\nСверяем по элементам...')
        equ = True
        for l_tss in tss:
            if l_tss not in real_timestamps:
                equ = False
        if not equ:
            print('--->НЕСОВПАДЕНИЕ!')
        else:
            print('--->Равны...')

if __name__ == '__main__':
    main()
