#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, gevent, re, requests
from time import sleep, time, strftime, localtime
from gevent.pool import Pool
from bs4 import BeautifulSoup
from bs4 import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from util.spider.freeproxy.commons import _headers, _user_agents, _executable_path, _sleep_time, load_file
from util.spider.freeproxy.db_utils import _clawer_db, create_connection
from util.spider.freeproxy.db_utils import update_tac_info, update_tac_status, insert_disable_proxy
from util.spider.freeproxy.db_utils import all_activate_proxies, load_imei, refresh_disable_proxies, update_proxy_error
from util.spider.freeproxy.client import load_from_db


def get_phone_data(table_tag: Tag) -> []:
    """
    从页面载入品牌和机型
    :param table_tag: 表格内容
    :return: [品牌,标签]
    """
    data = []

    if table_tag is not None:
        tr_list = table_tag.find_all('tr')
        tr_index = 0
        for tr in tr_list:
            # 品牌
            if tr_index == 1:
                td = tr.find('td')
                if td is not None:
                    text = str(td.get_text())
                    brand = text.replace('IMEIdb.com免费查询', '').replace('IMEIdb', '').strip()
                    data.append(brand)
            # 机型
            if tr_index == 2:
                td = tr.find('td')
                if td is not None:
                    text = str(td.get_text())
                    model = text.replace('IMEIdb.com免费查询', '').replace('IMEIdb', '').strip()
                    data.append(model)

            tr_index = tr_index + 1

    return data


def save_search_data(page_source: str, imei: str, proxy: str):
    row = []
    # 数据为初始化状态
    status = 1
    # 代理是否被禁用
    is_disable = False

    # 代理是否被禁用
    msg_list = re.findall('(您已经查询了很多次)', page_source)
    if len(msg_list) > 0:
        is_disable = True
    else:
        # 恰好尚未记录您的手机型号
        msg_list = re.findall('(恰好尚未记录您的手机型号)', page_source)
        if len(msg_list) > 0:
            status = 2
        else:
            # 暂时无法提供数据
            msg_list = re.findall('(暂时无法提供数据)', page_source)
            if len(msg_list) > 0:
                status = 3
            else:
                # 我们无法识别您输入的IMEI码
                msg_list = re.findall('(无法识别您输入的IMEI码)', page_source)
                if len(msg_list) > 0:
                    status = 4
                else:
                    # 读取品牌型号
                    page = BeautifulSoup(page_source, "lxml")
                    table = page.find('table')
                    data = get_phone_data(table)
                    # 查到品牌，机型
                    if len(data) > 1:
                        row += data
                        status = 0

        row += [status]

    # 将代理写入数据库
    conn = create_connection(_clawer_db)
    with conn:
        try:
            # 往表里写入禁用代理
            if is_disable:
                print('代理：' + proxy + ' 已不能使用')
                insert_disable_proxy(conn, (proxy,))
            else:
                tac = imei[0:8]
                if len(row) == 3:
                    # 写入品牌，机型
                    params = (row[0], row[1], row[2], tac)
                    print(params)
                    update_tac_info(conn, params)
                else:
                    # 查询出错的代理暂停使用一天
                    if status == 3:
                        insert_disable_proxy(conn, (proxy,))
                    # 写入数据状态
                    params = (row[0], tac)
                    print(params)
                    update_tac_status(conn, params)
        except Exception as e:
            print(e)


def search_imei_phantomjs(imei_list: [], proxy_list:[]) -> []:
    """
    查询imei并返回错误代理
    :param imei_list: imei列表
    :param proxy_list: 代理数据列表［代理,xp载入时间,xp]
    :return: 错误代理，[代理1, 代理2, ... , 代理n]
    """
    url = 'http://www.imeidb.com/#lookup'
    timeout = _sleep_time * 3

    errors = []

    for i in range(0, len(imei_list)):
        imei = imei_list[i]
        proxy_data = proxy_list[i]
        proxy = proxy_data[0]
        xp = proxy_data[2]

        sleep(random.uniform(int(_sleep_time / 2), _sleep_time))

        start_time = time()
        browser = None
        user_agent = random.choice(_user_agents)

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (user_agent)
        #dcap["phantomjs.page.settings.resourceTimeout"] = (timeout * 1000)
        # 默认为http代理，可以指定proxy type
        service_args = ['--proxy=' + proxy]
        service_args += ['--load-images=no', ]

        try:
            with gevent.Timeout(seconds=timeout * 2, exception=Exception('[Connection Timeout]')):
                query_url = 'http://www.imeidb.com/?xp=' + xp + '&imei=' + imei
                browser = webdriver.PhantomJS(executable_path=_executable_path,
                                              desired_capabilities=dcap,
                                              service_args=service_args)

                browser.set_page_load_timeout(timeout)
                browser.get(query_url)
                # 等待载入js
                WebDriverWait(browser, timeout).until(
                    expected_conditions.text_to_be_present_in_element(
                        (By.TAG_NAME, 'h1'),
                        'IMEIdb查询结果'
                    )
                )

                end_time = time()
                escaped = end_time - start_time
                print('代理：' + proxy + ' 网页：' + query_url + ' 用时：' + str(escaped))

                page_source = browser.page_source
                save_search_data(page_source, imei, proxy)

        except Exception as err:
            print(err)
            print('查找失败．imei:' + imei + ' proxy:' + proxy)
            errors.append(proxy)
        finally:
            if browser is not None:
                browser.quit()

    print('[IMEIdb查询结果] 查询个数:{:d} 代理错误个数:{:d}'.format(len(imei_list), len(errors)))
    return errors


def search_imei_chrome(imei_list: [], proxy_list:[]) -> []:
    """
    查询imei并返回错误代理
    :param imei_list: imei列表
    :param proxy_list: 代理数据列表［代理,xp载入时间,xp]
    :return: 错误代理，[代理1, 代理2, ... , 代理n]
    """
    url = 'http://www.imeidb.com/#lookup'
    timeout = _sleep_time * 6

    errors = []
    for i in range(0, len(imei_list)):

        imei = imei_list[i]
        proxy_data = proxy_list[i]
        proxy = proxy_data[0]
        xp = proxy_data[2]

        sleep(random.uniform(int(_sleep_time / 2), _sleep_time))

        start_time = time()
        browser = None
        user_agent = random.choice(_user_agents)

        dcap = dict(DesiredCapabilities.CHROME)
        dcap['proxy'] = {'proxyType': 'MANUAL',
                         'httpProxy': proxy,
                         'ftpProxy': proxy,
                         'sslProxy': proxy,
                         'noProxy': '',
                         'class': "org.openqa.selenium.Proxy",
                         'autodetect': False}
        dcap["chrome.switches"] = ["--user-agent=" + _user_agents[i]]
        #dcap["phantomjs.page.settings.userAgent"] = (user_agent)
        # dcap["phantomjs.page.settings.resourceTimeout"] = (timeout * 1000)
        # 默认为http代理，可以指定proxy type
        #service_args = ['--proxy=' + proxy]
        service_args = ['--load-images=no', ]

        try:
            with gevent.Timeout(seconds=timeout * 2, exception=Exception('[Connection Timeout]')):
                query_url = 'http://www.imeidb.com/?xp=' + xp + '&imei=' + imei
                browser = webdriver.Chrome(executable_path=_executable_path,
                                              desired_capabilities=dcap,
                                              service_args=service_args)

                browser.set_page_load_timeout(timeout)

                browser.get(query_url)
                # 等待载入js
                WebDriverWait(browser, timeout).until(
                    expected_conditions.text_to_be_present_in_element(
                        (By.TAG_NAME, 'h1'),
                        'IMEIdb查询结果'
                    )
                )

                end_time = time()
                escaped = end_time - start_time
                print('代理：' + proxy + ' 网页：' + query_url + ' 用时：' + str(escaped))

                page_source = browser.page_source
                save_search_data(page_source, imei, proxy)

        except Exception as err:
            print(err)
            print('查找失败．imei:' + imei + ' proxy:' + proxy)
            errors.append(proxy)
        finally:
            if browser is not None:
                browser.quit()

    print('[IMEIdb查询结果] 查询个数:{:d} 代理错误个数:{:d}'.format(len(imei_list), len(errors)))
    return errors


def get_imei() -> []:
    imei_list = []
    conn = create_connection(_clawer_db)
    with conn:
        try:
            data_list = load_imei(conn)
            for data in data_list:
                imei_list.append(data[0])
        except Exception as e:
            print(e)

    return imei_list


def get_proxies() -> []:
    data_list = []
    # 重新载入有效代理
    load_from_db()

    conn = create_connection(_clawer_db)
    with conn:
        try:
            # 取代理前先刷新禁用代理
            refresh_disable_proxies(conn)
            data_list = all_activate_proxies(conn)
        except Exception as e:
            print(e)

    print('载入' + str(len(data_list)) + '个代理')

    return data_list


def query_from_imeidb():
    thread_count = 2

    # 循环取imei进行查询
    for i in range(0, 50):
        # 查找limit设置为6
        imei_list = get_imei()
        imei_size = len(imei_list)
        proxy_list = get_proxies()
        sleep(_sleep_time * 3)
        data_list = []
        for j in range(0, imei_size):
            if (len(proxy_list) > 0):
                data_list.append(proxy_list.pop())

        if (len(data_list) == imei_size):
            # 查找并获取错误的代理
            str_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
            print(str_time + '开始抓取数据' + str(i))
            errors = search_imei_phantomjs(imei_list, data_list)
            # 有错误代理则更新代理库中的错误次数
            if (len(errors) > 0):
                params = []
                for proxy in errors:
                    params.append((proxy,))
                conn = create_connection(_clawer_db)
                with conn:
                    try:
                        update_proxy_error(conn, params)
                    except Exception as e:
                        print(e)
            str_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
            print(str_time + '结束抓取数据' + str(i))
            sleep(_sleep_time * 6)
        else:
            print("没有足够的代理")
            sleep(_sleep_time * 20)
            

def data_from_file(file: str):
    data_list = load_file(file)
    conn = create_connection(_clawer_db)
    with conn:
        for data in data_list:
            params = (data[4], data[5], 0, data[2])
            try:
                update_tac_info(conn, params)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    #data_from_file('/home/laomie/Downloads/tac_data.csv')
    query_from_imeidb()
