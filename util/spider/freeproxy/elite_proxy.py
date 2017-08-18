#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, csv, time, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def get_proxies(source: str) -> []:
    proxy_list = []

    page = BeautifulSoup(source, "lxml")
    table = page.find("table")
    tr_list = table.find_all("tr")
    tr_size = len(tr_list)

    # skip 2 tr
    for i in range(2, tr_size):
        tr = tr_list[i]
        td_list = tr.find_all("td")
        if (len(td_list) > 2):
            td_ip = td_list[1]
            ip_text = str(td_ip.get_text())
            ip_list = re.findall('.*?\)(\d+\.\d+\.\d+\.\d+).*?', ip_text)

            td_port = td_list[2]
            port_text = str(td_port.get_text())
            port_list = re.findall('.*?\)(\d+).*?', port_text)

            if (len(ip_list) > 0 and len(port_list) > 0):
                proxy_list.append([ip_list[0] + ':' + port_list[0]])

    return proxy_list

def load_page() -> []:
    proxy_list = []

    executable_path = r'/home/laomie/tools/phantomjs/bin/phantomjs'
    proxy_url = 'http://www.gatherproxy.com/proxylist/anonymity/?t=Elite#1'
    timeout = 90
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

    browser = None
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (user_agent)

    # use local proxy server
    service_args = ['--proxy=' + 'http://127.0.0.1:8087']
    service_args += ['--load-images=no', ]

    try:
        browser = webdriver.PhantomJS(executable_path=executable_path,
                                      desired_capabilities=dcap,
                                      service_args=service_args)

        browser.set_page_load_timeout(timeout)
        browser.get(proxy_url)

        #browser.implicitly_wait(10)
        # 等待载入js
        #WebDriverWait(browser, timeout).until(
        #    expected_conditions.text_to_be_present_in_element(
        #        (By.TAG_NAME, 'input'),
        #        'Show Full List'
        #    )
        #)

        # click "Show Full List" button
        browser.find_element_by_tag_name("form").find_element_by_class_name("button").click()
        print("get page 1 sleep 5")
        time.sleep(5)
        page_source = browser.page_source
        proxy_list += get_proxies(page_source)

        div = browser.find_element_by_class_name("pagenavi")
        links = div.find_elements_by_tag_name("a")
        page_size = len(links)
        print("page size:" + str(page_size))

        for index in range(0, page_size):
            link = links[index]
            link.click()
            div = browser.find_element_by_class_name("pagenavi")
            links = div.find_elements_by_tag_name("a")
            print("get page " + str(index + 2) + " sleep 5")
            time.sleep(5)
            page_source = browser.page_source
            proxy_list += get_proxies(page_source)

    except Exception as err:
        print(err)
    finally:
        if browser is not None:
            browser.quit()

    return proxy_list


def load_to_file(proxy_file: str):
    proxy_list = load_page()

    # write proxies to file
    with open(proxy_file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')
        writer.writerows(proxy_list)

"""
get elite proxies from http://www.gatherproxy.com/proxylist/anonymity/?t=Elite#1
"""
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        proxy_file = sys.argv[1]
        load_to_file(proxy_file)
    else:
        print("python elite_proxy.py [proxy_file]")