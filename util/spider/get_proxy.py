# -*- coding: utf-8 -*-

import sys, csv
import requests
from bs4 import BeautifulSoup
from bs4 import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

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

def load_imei(file: str) -> []:
    data_list = []

    with open(file, "r") as csv_input:
        reader = csv.reader(csv_input, delimiter='\t', lineterminator='\n')
        for row in reader:
            data_list.append(row)

    return data_list


def save_phone_data(file: str, data_list: []):
    with open(file, "w") as csv_output:
        writer = csv.writer(csv_output, delimiter=',', lineterminator='\n')
        writer.writerows(data_list)


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
                    data.append(str(td.get_text()))
            # 机型
            if tr_index == 2:
                td = tr.find('td')
                if td is not None:
                    data.append(str(td.get_text()))

            tr_index = tr_index + 1

    return data


def search_imei(imei: str, proxy:str) -> []:
    data = []
    ip = proxy.split(':')[0]
    port = proxy.split(':')[1]

    fp = webdriver.FirefoxProfile()
    # Direct = 0, Manual = 1, PAC = 2, AUTODETECT = 4, SYSTEM = 5
    fp.set_preference("network.proxy.type", 1)
    fp.set_preference("network.proxy.http", ip)
    fp.set_preference("network.proxy.http_port", int(port))
    fp.set_preference("general.useragent.override", _user_agents[6])
    fp.update_preferences()

    try:

        browser = webdriver.Firefox(executable_path=r'/home/laomie/tools/geckodriver', firefox_profile=fp)
        browser.set_page_load_timeout(60)
        #browser = webdriver.Firefox(executable_path=r'/home/laomie/tools/geckodriver')
        browser.get('http://www.imeidb.com/#lookup')
        imei_text = browser.find_element_by_name("imei")
        imei_text.send_keys(imei)

        browser.find_element_by_tag_name("form").find_element_by_tag_name("button").click()

        WebDriverWait(browser, 20).until(
            expected_conditions.text_to_be_present_in_element(
                (By.TAG_NAME, 'h1'),
                'IMEIdb查询结果'
            )
        )

        page = BeautifulSoup(browser.page_source, "lxml")
        table = page.find('table')
        data = get_phone_data(table)
    except Exception as err:
        print('查找失败．imei:' + imei + ' proxy:' + proxy)
    finally:
        if browser is not None:
            #browser.quit()
            print('end')

    return data


def load_proxy(data_list: []) -> []:
    proxy_list = []
    ip_url = 'http://icanhazip.com/'

    for data in data_list:
        proxy = 'http://' + data[0]
        type = data[1]
        if (type == "HTTP"):
            proxies = {
                'http': proxy,
                'https': proxy,
            }
            try:
                r = requests.get(ip_url, proxies=proxies, timeout=2)
                proxy_list.append(data[0])
            except Exception as err:
                print('timeout: ' + proxy)

    return proxy_list


def proxy_from_web() -> []:
    data_list = []
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}

    #for step in range(0, 578):
    for i in range(1041, 1042):
        #url = "http://proxydb.net/?offset=" + str(offset)
        url = "http://www.xicidaili.com/nn/" + str(i)
        print('载入代理：' + url)
        content = requests.get(url, headers=headers).text
        page = BeautifulSoup(content, "lxml")

        table = page.find('table')

        if table is not None:
            #tbody = table.find('tbody')
            tr_list = table.find_all('tr')
            index = 0
            for tr in tr_list:
                if (index > 0):
                    if (len(tr.contents) > 11):
                        proxy = str(tr.contents[3].text).strip()
                        port = str(tr.contents[5].text).strip()
                        type = str(tr.contents[11].text).strip()
                        data_list.append([proxy + ':' + port, type])
                index = index + 1
    return data_list


def load_from_imeidb(imei_file: str, data_file: str):
    # 查询后取得的数据列表
    data_list = []

    # 网上获取可用的代理
    #proxy_data = proxy_from_web()
    #proxy_list = load_proxy(proxy_data)
    proxy_list = ['136.144.129.163:8888']
    print(len(proxy_list))

    ''''''
    index = 0
    # 载入imei数据
    imei_list = load_imei(imei_file)

    for row in imei_list:
        if (row is not None) and (len(row) > 0):
            imei = row[1]
            proxy = proxy_list[0]
            data = search_imei(imei, proxy)
            print(imei)
            print(data)
            # 查到imei机型等则输出
            if (len(data) == 2):
                data_list.append(row + data)

        index = index + 1

    save_phone_data(data_file, data_list)
    ''''''

if __name__ == '__main__':
    if (len(sys.argv) > 2):
        imei_file = sys.argv[1]
        data_file = sys.argv[2]
        load_from_imeidb(imei_file, data_file)
    else:
        print("usage: python imei_info.py imei_file data_file")