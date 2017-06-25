#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cloned from  https://github.com/YieldNull/freeproxy.git
"""
from gevent import monkey

monkey.patch_socket()

import gevent
import re
import requests
import random
from time import time, sleep, localtime, strftime
from gevent.pool import Pool
from util.spider.freeproxy.proxy import fetch_proxies
from util.spider.freeproxy.commons import _headers, _user_agents, _executable_path, _sleep_time
from util.spider.freeproxy.db_utils import _clawer_db, create_connection, upsert_proxy, reload_activate_proxies, all_proxy


def validate_proxies(proxies: [], timeout=15) -> []:
    """
    Test proxies, or process html source using callback in the meantime.

    :type proxies: list
    :param proxies:  proxies
    :param timeout: response timeout
    :return: [(proxy1, response_time1), (proxy2, response_time2),...,(proxyn, response_timen)]
    """
    test_url = 'http://www.imeidb.com/#lookup'
    result = []
    proxies = set(proxies)
    errors = set()
    pool = Pool(100)

    def load(proxy):
        code = None
        is_success = False
        sleep(random.uniform(0, 0.1))

        start_time = time()
        str_time = strftime('%Y-%m-%d %H:%M:%S', localtime(start_time))
        print(str_time + '开始测试代理' + proxy)
        try:
            with gevent.Timeout(seconds=timeout, exception=Exception('[Connection Timeout]')):
                _headers['User-Agent'] = random.choice(_user_agents)
                proxies = {'http': 'http://{}'.format(proxy.strip()),
                    'https': 'https://{}'.format(proxy.strip())}

                res = requests.get(test_url, proxies=proxies, headers=_headers)
                code = res.status_code
                source = res.text
                #welcome = re.findall('(<h1>欢迎来到IMEIdb</h1>)', source)
                xp = re.findall('input type="hidden" name="xp" value="(.*?)"', source)
                if len(xp) > 0:
                    is_success = True

            if code != 200:
                errors.add(proxy)

        except Exception as e:
            # log(e.args)
            errors.add(proxy)

        end_time = time()

        if code == 200 and is_success:
            escaped = end_time - start_time
            result.append((proxy, round(escaped, 2)))

    index = 0
    for proxy in proxies:
        pool.spawn(load, proxy)
        index += 1
        if index % 100 == 0:
            sleep(random.uniform(int(_sleep_time / 8), int(_sleep_time / 4)))
    pool.join()

    proxies = proxies - errors
    print('[HTTP Proxies] Available:{:d} Deprecated:{:d}'.format(len(proxies), len(errors)))

    return result


def load_from_web():
    web_proxies = fetch_proxies()
    proxies = validate_proxies(web_proxies)
    proxy_list = [l[0:1] for l in proxies]
    # 将代理写入数据库
    conn = create_connection(_clawer_db)
    with conn:
        try:
            # 有效代理并入代理表
            print('有效代理并入数据库')
            upsert_proxy(conn, proxy_list)
            # 重生成有效代理表数据
            print('重新载入有效代理')
            reload_activate_proxies(conn, proxies)
        except Exception as e:
            print(e)


def load_from_db():
    # 从数据库载入所有可用的代理并测试
    db_proxies = []
    conn = create_connection(_clawer_db)
    with conn:
        try:
            all_proxies = all_proxy(conn)
            if all_proxies is not None:
                for db_proxy in all_proxies:
                    db_proxies += db_proxy
        except Exception as e:
            print(e)

    proxies = validate_proxies(db_proxies)

    # 将代理写入数据库
    conn = create_connection(_clawer_db)
    with conn:
        try:
            # 重新载入有效代理表数据
            print('重新载入有效代理')
            reload_activate_proxies(conn, proxies)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    #test_url = 'http://icanhazip.com/'
    load_from_web()