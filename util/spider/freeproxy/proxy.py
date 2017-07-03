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
    base = 'http://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:{:d}'
    urls = [base.format(i) for i in range(1, 16)]

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
    From "http://proxydb.net/?protocol=http&anonlvl=4&availability=30&response_time=30&offset=0"
    :return:
    """
    base = 'http://proxydb.net/?protocol=http&anonlvl=4&availability=30&response_time=30&offset={:d}'
    urls = [base.format(i * 15) for i in range(0, 17)]

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
    urls = [base.format(i) for i in range(1, 51)]
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
                if (type == '高匿'):
                    proxies += ['{:s}:{:s}'.format(host, port)]
        except Exception as e:
            print(e)

    return proxies


def fetch_proxies():
    """
    Get latest proxies from above sites.
    """
    functions = [
        from_cool_proxy,
        from_proxydb,
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

"""
https://hidemy.name/en/proxy-list/?type=h&anon=4#list
https://hidemy.name/en/proxy-list/?type=h&anon=4&start=64#list

<td class=tdl>47.90.204.6</td><td>8080</td>

https://premproxy.com/list/01.htm

<td>139.59.174.207:8118</td><td>high-anonymous </td>

http://rebro.weebly.com/txt-lists.html

<a href="/uploads/2/7/3/7/27378307/rebroproxy-100-103221072014.txt">

http://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1


http://www.gatherproxy.com/proxylist/anonymity/?t=Elite#1
https://www.proxynova.com/proxy-server-list/elite-proxies/
"""
