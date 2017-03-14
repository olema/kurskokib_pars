#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Выборка сообщений на модерации со страницы отзывов на сайте
# http://kurskokib.ru
# Планируется:
#   - по наличию новых сообщений выставлять файл-флаг по пути
#       из файла reviews.config;
#   - отправлять email на адреса из reviews.config;
#
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
import smtplib
import time
import os.path


def mail_send(fromaddr, toaddr, subject, message):
    '''Функция отправки письма'''
    from_header = 'From: router2 <{}>\r\n'.format(fromaddr)
    string_toaddr = ','.join(['<' + i + '>' for i in toaddr])
    to_header = 'To: recipients {}\r\n'.format(string_toaddr)
    subject_header = 'Subject: {}\r\n'.format(subject)
    msg = '{}{}{}\n{}'.format(from_header, to_header, subject_header, message)
    server = smtplib.SMTP('linuxserver.internal.kurskokib.ru')
    server.sendmail(fromaddr, toaddr, msg)
    server.quit()
    # print(msg)


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
        logging.error("Ошибка в параметрах командной строки")
        return False
    else:
        return True


def config(confname):
    ''' Работа с конфигом reviews.config с помощью модуля configparser.
        Возвращает словарь с переменными из конфига confname
    '''

    dict_var = dict()

    # Проверка существования файла из confname.
    # Если файла нет, возвращаем пустой словарь
    if not os.path.exists(confname):
        return dict_var

    config = configparser.ConfigParser()
    config.read(confname)
    sections = config.sections()
    for k in sections:
        for s in config[k]:
            dict_var[s] = config[k][s]
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
    fromaddr = 'semashko@kursktelecom.ru'
    toaddr = ['matushkin.oleg@gmail.com', 'okibkursk-it@yandex.ru']
    subject = 'Reviews in kurskokib.ru: ' + time.strftime('%a, %d %b %Y %H:%M:%S')
    message = '''Something error...
    Check reviews parser log on server...'''


    # Инициализация подсистемы логирования
    #
    if not log_init():
        mail_send(fromaddr, toaddr, subject, message)
        exit(-1)

    # Проверяем параметры коммандной строки
    #
    if not check_cmd():
        logging.error("Wrong cmd parameters...")
        message = '''Error: Wrong cmd parameters...'''
        mail_send(fromaddr, toaddr, subject, message)
        exit(-1)

    # Загружаем пременные из конфигруационного файла reviews.config
    # Если файла нет - выходим с ошибкой
    #
    dvar = config('reviews.config')
    if not dvar:
        logging.error(u'No parameters in config file...')
        message = '''Error: No parameters in config file...'''
        exit(-1)

    logging.info(u'Start testing reviews on {}.'.format(sys.platform))

    # Читаем переменные из файла конфигурации
    # dvar - словарь

    # Если есть email-ы из review.config, то заменяем toaddr на них
    #
    if 'email' in dvar:
        toaddr = []
        for k in dvar:
            if 'email' in k:
                toaddr.append(dvar[k])

    # Читаем страницу с сайта
    s = requests.session()
    data = {"ln": sys.argv[1], "pd": sys.argv[2]}
    try:
        r = s.post(dvar['url_admin'], data=data)
        status_code = r.status_code
    except:
        status_code = 300

    # Если сайт вернул не 200
    if status_code != 200:
        logging.error('Site return status code {}'.format(status_code))
        message = '''Site return status code {}.
        URL of administration page: http://kurskokib.ru/page_edit/_samples/admin.php
        '''.format(status_code)
        mail_send(fromaddr, toaddr, subject, message)
        return -1

    r = s.get(dvar['url_rev'])

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

    # Сформируем список таймстампов текущего состояния страницы
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

    print('On previous page ' + str(len(tss)) + ' reviews')
    logging.info(u'On previous page ' + str(len(tss)) + ' reviews...')

    message = '''Check finished...
        URL of administration page:
        http://kurskokib.ru/page_edit/_samples/admin.php'''

    # Подготовка данных для отправки email
    # Проверяем новые отзывы
    #   tss - список со старыми
    #   real_timestamps - новый список
    print('\nСравниваем кол-во элементов..."')
    if len(tss) != len(real_timestamps):
        print('---> НЕ РАВНЫ! ')
        # Отправляем письмо, что кол-во элементов изменилось
        message = '''The number of items on the page has changed.
                URL of administration page:
                http://kurskokib.ru/page_edit/_samples/admin.php'''
        # Пишем в log
        logging.info('The number of items on the page has changed.')
        # Формируем новый список tss (таймстампов для хранения)
        f = open('timestamps', 'w')
        for l in real_timestamps:
            f.write(l+'\n')
        f.close()
        logging.info(u'New timestamps file is created.')

    # если равны по количеству, сверяем по элементам
    else:
        print('---> Равны...')
        print('\nСверяем по элементам...')
        equ = True
        for l_tss in tss:
            if l_tss not in real_timestamps:
                equ = False
                nequ_tss = l_tss
        if not equ:
            print('--->НЕСОВПАДЕНИЕ!')
            message = '''The items on the page has changed ({}).
            URL of administration page:
            http://kurskokib.ru/page_edit/_samples/admin.php'''.format(nequ_tss)
            # Пишем в log
            logging.info(u'The items on the page has changed.')
            # Формируем новый список tss (таймстампов для хранения)
            f = open('timestamps', 'w')
            for l in real_timestamps:
                f.write(l+'\n')
            f.close()
            logging.info(u'New timestamps file is created.')
        else:
            print('--->Равны...')

    mail_send(fromaddr, toaddr, subject, message)

if __name__ == '__main__':
    main()
