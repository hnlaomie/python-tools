from bs4 import BeautifulSoup
import os, requests

class MLWeb():
    def print_links(self, url: str) :
        html = self.request(url)
        item_list = BeautifulSoup(html.text, 'lxml').find_all('a')
        for item in item_list:
            if item is not None:
                down_url = str(item.get('href'))
                if not down_url.startswith("https://www.youtube"):
                    down_url = "http://speech.ee.ntu.edu.tw/~tlkagk/" + down_url
                if not down_url.endswith("html"):
                    print(down_url)

    def request(self, url):  ##这个函数获取网页的response 然后返回
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
        # content.encoding需要和BeautifulSoup的'utf-8'一致，否则乱码
        content = requests.get(url, headers=headers)
        return content

web = MLWeb()
web.print_links('http://speech.ee.ntu.edu.tw/~tlkagk/courses_MLDS17.html')