#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
import re
import requests
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from util.spider.freeproxy.commons import _headers, _user_agents, _executable_path

def search_imei(imei: str, proxy: str):
    start_time = time.time()
    url = 'http://www.imeidb.com/#lookup'
    try:
        with gevent.Timeout(seconds=10, exception=Exception('[Connection Timeout]')):
            _headers['User-Agent'] = random.choice(_user_agents)
            proxies = {'http': 'http://{}'.format(proxy.strip()),
                    'https': 'https://{}'.format(proxy.strip())}

            res = requests.get(url,
                proxies=proxies,
                headers=_headers
            )
            code = res.status_code
            source = res.text
            # welcome = re.findall('(<h1>欢迎来到IMEIdb</h1>)', source)
            xp = re.findall('input type="hidden" name="xp" value="(.*?)"', source)
            if len(xp) > 0:
                print(xp)
                time.sleep(5)
                query_url = 'http://www.imeidb.com/?xp=' + xp[0] + '&imei=' + imei

                # 用PhantomJS通过代理查询
                dcap = dict(DesiredCapabilities.PHANTOMJS)
                dcap["phantomjs.page.settings.userAgent"] = (random.choice(_user_agents))
                # dcap["phantomjs.page.settings.resourceTimeout"] = (timeout * 1000)
                # 默认为http代理，可以指定proxy type
                service_args = ['--proxy=' + proxy]
                service_args += ['--load-images=no',]
                browser = webdriver.PhantomJS(executable_path=_executable_path,
                                              desired_capabilities=dcap,
                                              service_args=service_args)

                browser.set_page_load_timeout(60)
                browser.get(query_url)
                print('等待载入js...')
                WebDriverWait(browser, 60).until(
                    expected_conditions.text_to_be_present_in_element(
                        (By.TAG_NAME, 'h1'),
                        'IMEIdb查询结果'
                    )
                )
                source = browser.page_source

                '''
                # 用requests查，无法通过js载入查询结果
                data = {"xp":xp[0] , "imei":imei}
                res = requests.get(query_url,
                    proxies=proxies,
                    headers=_headers,
                    params=data,
                    data=data
                )
                source = res.text
                '''
                print(source)


        if code != 200:
            print('status code:' + str(code))

    except Exception as e:
        # log(e.args)
        print(e)

    end_time = time.time()
    escaped = end_time - start_time
    print(escaped)

search_imei('867148029999884', '61.130.97.212:8099')