#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cloned from  https://github.com/YieldNull/freeproxy.git
"""

import os, csv
import logging
import requests
import random
import gevent
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# http request headers
_headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
}

# http request user-agent
_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36 OPR/36.0.2130.32',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.10551.6 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 4.4.4; HTC D820mt Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0; Google Nexus 5 - 5.0.0 - API 21 - 1080x1920 Build/LRX21M) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
]

_use_logging = False
_logger = None
_sleep_time = 20
_executable_path = r'/home/laomie/tools/phantomjs/bin/phantomjs'

_home_dir = os.path.join(os.path.expanduser("~"), '.crawler')
if not os.path.exists(_home_dir):
    os.mkdir(_home_dir)

# Disable warning.
logging.getLogger("requests").setLevel(logging.ERROR)
requests.packages.urllib3.disable_warnings()


def _safe_http(url, data=None, session=None, proxies=None, timeout=20, want_obj=False):
    """
    Get the HTML source at url.
    :param url: url
    :param data: data of POST as dict
    :param session: send http requests in the session
    :param proxies: send http requests using proxies
    :param timeout: response timeout, default is 10s
    :param want_obj: return a response object instead of HTML source or not. Default is False.
    :return: The HTML source or response obj. If timeout or encounter exception, return '' or None(want_obj is set True).
    """
    _headers['User-Agent'] = random.choice(_user_agents)
    try:
        with gevent.Timeout(seconds=timeout, exception=Exception('[Connection Timeout]')):
            if data is None:
                res = requests.get(url, headers=_headers, proxies=proxies) if session is None \
                    else session.get(url, headers=_headers, proxies=proxies)
            else:
                res = requests.post(url, headers=_headers, data=data, proxies=proxies) if session is None \
                    else session.post(url, headers=_headers, data=data, proxies=proxies)

        code = res.status_code
        #_log('[{:d}] {:s} {:s}'.format(code, 'POST' if data is not None else 'GET', url))

        if want_obj:
            return res
        else:
            return res.text if code == 200 else ''
    except Exception as e:
        # log(e.args)
        #_log('[{:s}] {:s} {:s}'.format('HTTP Error', 'POST' if data is not None else 'GET', url))
        return None if want_obj else ''


def _safe_phantomjs(url, proxy=None, timeout=120):
    """
    Get the HTML source at url.
    :param url: url
    :param proxy: send http requests using proxies
    :param timeout: response timeout, default is 10s
    :return: The HTML source. If timeout or encounter exception, return '').
    """
    html_source = ''
    browser = None

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (random.choice(_user_agents))
    dcap["phantomjs.page.settings.resourceTimeout"] = (timeout * 1000)
    # 默认为http代理，可以指定proxy type
    service_args = None if proxy is None else ['--proxy=' + proxy]
    try:
        with gevent.Timeout(seconds=timeout, exception=Exception('[Connection Timeout]')):
            browser = webdriver.PhantomJS(executable_path=_executable_path,
                                          desired_capabilities=dcap) if proxy is None \
            else webdriver.PhantomJS(executable_path=_executable_path,
                                     desired_capabilities=dcap,
                                     service_args=service_args)
            browser.get(url)
            html_source = browser.page_source

    except Exception as e:
        # log(e.args)
        #_log('[{:s}] {:s} {:s}'.format('HTTP Error', 'POST' if data is not None else 'GET', url))
        print(e)
        print('[{:s}] {:s} {:s}'.format('HTTP Error', 'GET', url))
    finally:
        if browser is not None:
            browser.quit()

    return html_source


def load_file(file: str, delimiter: str = ',') -> []:
    data_list = []

    with open(file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter=delimiter, lineterminator='\n')
        for row in reader:
            data_list.append(row)

    return data_list


def _init_logger():
    from logging.handlers import RotatingFileHandler

    # logging file "~/.freeproxy/freeproxy.log"
    log_file = os.path.join(_home_dir, 'freeproxy.log')

    # logger config
    handler = RotatingFileHandler(log_file, mode='a', maxBytes=50 * 1024 * 1024, backupCount=2)
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    handler.setLevel(logging.INFO)

    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def _log(msg):
    if _use_logging and _logger:
        _logger.info(msg)
    else:
        print(msg)


def enable_logging():
    global _use_logging
    _use_logging = True
