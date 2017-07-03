# -*- coding: utf-8 -*-

import sys, csv, random
from time import sleep, time, localtime, strftime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from util.spider.ip_utils.db_utils import blank_edu_ip, update_begin_ip_desc, update_end_ip_desc
from util.spider.ip_utils.db_utils import _clawer_db, create_connection

_executable_path = r'/home/laomie/tools/phantomjs/bin/phantomjs'
_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36 OPR/36.0.2130.32',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.10551.6 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 4.4.4; HTC D820mt Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0; Google Nexus 5 - 5.0.0 - API 21 - 1080x1920 Build/LRX21M) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.0.2564.116 Chrome/48.0.2564.116 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
]

def get_ip_desc(ip: str) -> str:

    browser = None
    desc = ''
    user_agent = random.choice(_user_agents)
    print(user_agent)
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (user_agent)

    try:
        url = 'https://www.ipip.net/ip.html'
        browser = webdriver.PhantomJS(executable_path=_executable_path,
            desired_capabilities=dcap)
        browser.set_page_load_timeout(50)
        browser.get(url)

        ip_input = browser.find_element_by_id("ip")
        print(ip_input.text)
        ip_input.send_keys(ip)

        browser.find_element_by_tag_name("form").find_element_by_tag_name("button").click()

        wait = WebDriverWait(browser, 30)
        element = wait.until(
            expected_conditions.visibility_of_element_located(
                (By.ID, 'myself')
            )
        )

        desc = element.text


    except Exception as err:
        print(err)
        print('查找失败．ip:' + ip)
    finally:
        if browser is not None:
            browser.quit()

    return desc


def load_ip_desc():
    ip_list = []
    conn = create_connection(_clawer_db)
    with conn:
        try:
            data_list = blank_edu_ip(conn)
            for row in data_list:
                if row is not None and len(row) > 1:
                    ip_list.append([row[0], row[1]])
        except Exception as e:
            print(e)

    begin_param_list = []
    end_param_list = []
    for ip in ip_list:
        sleep(2)
        begin_desc = get_ip_desc(ip[0])
        print("ip:" + ip[0] + " desc:" + begin_desc)
        begin_param_list.append((begin_desc, ip[0],))
        sleep(2)
        end_desc = get_ip_desc(ip[1])
        print("ip:" + ip[1] + " desc:" + end_desc)
        end_param_list.append((end_desc, ip[1],))

    if len(begin_param_list) > 0:
        conn = create_connection(_clawer_db)
        with conn:
            try:
                update_begin_ip_desc(conn, begin_param_list)
                update_end_ip_desc(conn, end_param_list)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    for i in range(1, 51):
        start_time = time()
        str_time = strftime('%Y-%m-%d %H:%M:%S', localtime(start_time))
        print(str_time + '开始抓取数据' + str(i))

        load_ip_desc()

        end_time = time()
        escaped = end_time - start_time
        print('第' + str(i) + '次抓取用时：' + str(escaped))
