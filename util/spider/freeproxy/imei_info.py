#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, gevent, re, requests
from time import sleep, time
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
                    #if status == 3:
                    #    insert_disable_proxy(conn, (proxy,))
                    # 写入数据状态
                    params = (row[0], tac)
                    print(params)
                    update_tac_status(conn, params)
        except Exception as e:
            print(e)


def search_imei(imei_list: [], proxy_list:[], thread_count: int) -> []:
    """
    查询imei并返回错误代理
    :param imei_list: imei列表
    :param proxy_list: 代理列表
    :param thread_count: 启动线程数
    :return: 错误代理，[代理1, 代理2, ... , 代理n]
    """
    url = 'http://www.imeidb.com/#lookup'
    timeout = _sleep_time * thread_count

    errors = []
    pool = Pool(thread_count)

    def search(imei: str, proxy: str):

        sleep(random.uniform(1, int(_sleep_time / thread_count)))
        start_time = time()
        browser = None

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (random.choice(_user_agents))
        #dcap["phantomjs.page.settings.resourceTimeout"] = (timeout * 1000)
        # 默认为http代理，可以指定proxy type
        service_args = ['--proxy=' + proxy]
        service_args += ['--load-images=no', ]

        try:

            with gevent.Timeout(seconds=timeout * 2, exception=Exception('[Connection Timeout]')):
                # 从查询页面找出"xp"值，用它构建查询的url
                _headers['User-Agent'] = random.choice(_user_agents)
                proxies = {'http': 'http://{}'.format(proxy.strip()),
                           'https': 'https://{}'.format(proxy.strip())}
                res = requests.get(url, proxies=proxies, headers=_headers)
                code = res.status_code

                # 能正确打开页面，则取出"xp"值
                if code == 200:
                    source = res.text
                    xp = re.findall('input type="hidden" name="xp" value="(.*?)"', source)

                    if len(xp) > 0:
                        query_url = 'http://www.imeidb.com/?xp=' + xp[0] + '&imei=' + imei
                        sleep(random.uniform(int(_sleep_time / thread_count), int(_sleep_time / thread_count * 2)))
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

    for i in range(0, len(imei_list)):
        imei = imei_list[i]
        proxy = proxy_list[i]

        pool.spawn(search, imei, proxy)
    pool.join()

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


def get_proxies(size: int) -> []:
    proxy_list = []
    # 重新载入有效代理
    load_from_db()

    # 代理需要达到指定个数
    while (len(proxy_list) < size):
        if (len(proxy_list) == 0):
            sleep(_sleep_time * 2)
        else:
            sleep(_sleep_time * 60)

        conn = create_connection(_clawer_db)
        with conn:
            try:
                # 取代理前先刷新禁用代理
                refresh_disable_proxies(conn)
                data_list = all_activate_proxies(conn)
                for data in data_list:
                    proxy_list.append(data[0])
            except Exception as e:
                print(e)

        print('载入' + str(len(proxy_list)) + '个代理')

    return proxy_list


def query_from_imeidb():
    thread_count = 8

    # 循环取imei进行查询
    for i in range(0, 1000):
        all_proxy = get_proxies(thread_count * 10)

        for idx in range(0, 5):
            # 查找limit设置为16
            imei_list = get_imei()
            proxy_list = []
            for imei in imei_list:
                proxy_list.append(all_proxy.pop())

            # 查找并获取错误的代理
            print(imei_list)
            errors = search_imei(imei_list, proxy_list, thread_count)
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

            sleep(_sleep_time * 4)


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
