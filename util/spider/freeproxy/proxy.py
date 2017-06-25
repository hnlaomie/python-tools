#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cloned from  https://github.com/YieldNull/freeproxy.git
"""

import re, codecs, base64, random


from time import sleep
from util.spider.freeproxy.commons import _headers, _user_agents, _sleep_time, _safe_http, _safe_phantomjs
from util.spider.freeproxy.db_utils import _clawer_db, create_connection, all_proxy

def from_cyber_syndrome():
    """
    From "http://www.cybersyndrome.net/"
    :return:
    """
    urls = [
        'http://www.cybersyndrome.net/pld6.html',
        'http://www.cybersyndrome.net/pla6.html'
    ]

    proxies = []
    for url in urls:
        print("load " + url)
        sleep(random.uniform(int(_sleep_time / 2), _sleep_time))
        try:
            res = _safe_phantomjs(url)
            proxies += re.findall('(\d+\.\d+\.\d+\.\d+:\d+)', res)
        except Exception as e:
            print(e)

    return proxies


def from_cool_proxy():
    """
    From "http://www.cool-proxy.net/proxies/http_proxy_list/sort:score/direction:desc/page:1"
    :return:
    """
    proxies = []
    base = 'http://www.cool-proxy.net/proxies/http_proxy_list/sort:score/direction:desc/page:{:d}'
    urls = [base.format(i) for i in range(1, 21)]

    proxies = []
    for url in urls:
        print("load " + url)
        sleep(random.uniform(int(_sleep_time / 2), _sleep_time))

        try:
            res = _safe_http(url)
            proxies += re.findall('(\d+\.\d+\.\d+\.\d+:\d+)', res)
            data = re.findall('<td .*?><script type="text/javascript">.*?"(.*?)".*?</script></td>.*?<td>(\d+)</td>', res, re.DOTALL)
            for (host, port) in data:
                # << Prev   1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9...22   Next >>
                ip = base64.b64decode(codecs.encode(host, 'rot13'))
                proxies.append(str(ip, 'utf-8') + ":" + port)
        except Exception as e:
            print(e)

    return proxies


def from_proxydb():
    """
    From "http://proxydb.net/?protocol=http&availability=50&response_time=10&offset=0"
    :return:
    """
    base = 'http://proxydb.net/?protocol=http&availability=50&response_time=10&offset={:d}'
    urls = [base.format(i * 15) for i in range(0, 33)]

    proxies = []
    for url in urls:
        print("load " + url)
        sleep(random.uniform(int(_sleep_time / 2), _sleep_time))

        try:
            res = _safe_http(url)
            proxies += re.findall('(\d+\.\d+\.\d+\.\d+:\d+)', res)
        except Exception as e:
            print(e)

    return proxies


def from_xici_daili():
    """
    From "http://www.xicidaili.com/"
    :return:
    """
    base = 'http://www.xicidaili.com/wt/{:d}'
    urls = [base.format(i) for i in range(1, 201)]
    """
    urls = [
        'http://www.xicidaili.com/nt/1',
        'http://www.xicidaili.com/nt/2',
        'http://www.xicidaili.com/nn/1',
        'http://www.xicidaili.com/nn/2',
        'http://www.xicidaili.com/wn/1',
        'http://www.xicidaili.com/wn/2',
        'http://www.xicidaili.com/wt/1',
        'http://www.xicidaili.com/wt/2'
    ]
    """

    proxies = []

    for url in urls:
        print("load " + url)
        sleep(random.uniform(int(_sleep_time / 2), _sleep_time))

        try:
            res = _safe_http(url)
            data = re.findall('<td>(\d+\.\d+\.\d+\.\d+)</td>.*?<td>(\d+)</td>.*?<td.*?>(高匿|透明)</td>.*?', res, re.DOTALL)
            for (host, port, type) in data:
                proxies += ['{:s}:{:s}'.format(host, port)]
        except Exception as e:
            print(e)

    return proxies


def fetch_proxies():
    """
    Get latest proxies from above sites.
    """
    functions = [
        from_cyber_syndrome,
        from_proxydb,
        from_xici_daili,
        from_cool_proxy,
    ]

    proxies = []
    for func in functions:
        pro = func()
        #_log('[{:s}] {:d} proxies'.format(func.__name__, len(pro)))
        if (len(pro) > 0):
            proxies += pro

    # 从数据库载入用过的有效代理
    conn = create_connection(_clawer_db)
    with conn:
        try:
            db_proxies = all_proxy(conn)
            if db_proxies is not None:
                for db_proxy in db_proxies:
                    proxies += db_proxy
        except Exception as e:
            print(e)

    return proxies

#fetch_proxies()
