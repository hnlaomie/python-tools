from bs4 import BeautifulSoup
import os, requests

class BQGBook():
    def init_sc_url(self, page_url: str) -> [] :
        a_style = 'word-wrap: break-word; text-decoration: none; color: rgb(0,153,204); line-height: normal'

        book_url_list = []
        html = self.request(page_url)  ##调用request函数把套图地址传进去会返回给我们一个response
        all_book_tag = BeautifulSoup(html.text, 'lxml').find_all('a')

        for a_tag in all_book_tag:
            if a_tag is not None:
                if a_tag.get('style') == a_style :
                    book_url = a_tag.get('href')
                    book_url_list.append(book_url)

        print(book_url_list)
        return book_url_list

    def init_page_url(self, first_page_url: str) -> [] :
        page_list = []
        page_stack = []
        page_stack.append(first_page_url)

        while page_stack:
            page_url = page_stack.pop()
            page_list.append(page_url)
            html = self.request(page_url)
            page_div = BeautifulSoup(html.text, 'lxml').find('div', class_='ch_pagebar').find_all('a')
            for a_tag in page_div:
                text = str(a_tag.get_text().encode('ISO-8859-1').decode('utf-8'))
                if (text == "下一页"):
                    next_page = "http://www.en8848.com.cn/" + a_tag.get('href')
                    page_stack.append(next_page)

        return page_list

    def init_book_url(self, page_url: str) -> [] :
        div_class = 'yd-book-content yd-book-content-standalone yd-store-content-container clearfix'
        book_div_class = 'yd-book-item yd-book-item-pull-left'

        book_url_list = []
        html = self.request(page_url)  ##调用request函数把套图地址传进去会返回给我们一个response
        all_book_div = BeautifulSoup(html.text, 'lxml').find('div', class_=div_class).find_all('div', class_=book_div_class)

        for div in all_book_div:
            a_tag = div.a
            if a_tag is not None:
                book_url = "http://www.en8848.com.cn/" + a_tag.get('href')
                book_url_list.append(book_url)

        print(book_url_list)
        return book_url_list

    def download(self, url: str):
        page_list = self.init_sc_url(url)
        #for page in page_list:
            #book_url_list = self.init_book_url(page)
        for book_url in page_list:
            try:
                self.download_file(book_url)
            except Exception as e:
                print(e)

    def download_file(self, book_url: str):
        ##调用request函数把套图地址传进去会返回给我们一个response
        html = self.request(book_url)
        item_list = BeautifulSoup(html.text, 'lxml').find_all('a')

        for item in item_list:
            down_url = "http://www.biquge.com" + item.get('href')
            print(item)
            '''
            html = self.request(down_url)

            title = BeautifulSoup(html.text, 'lxml').title.contents[0]
            title = str(title).replace("/", "-")
            a_tag_file = BeautifulSoup(html.text, 'lxml').find('a', id='dload')

            if a_tag_file is not None :
                file_url = "http://www.en8848.com.cn/e/DownSys/" + a_tag_file.get('href')[3:]
                print(title + " : " + file_url)
                html = self.request(file_url)
                f = open('/home/laomie/temp/enbooks/' + title + '.rar', 'ab')
                f.write(html.content)
                f.close()
            '''

    def html(self, href):  ##这个函数是处理套图地址获得图片的页面地址
        html = self.request(href)
        max_span = BeautifulSoup(html.text, 'lxml').find_all('span')[10].get_text()
        for page in range(1, int(max_span) + 1):
            page_url = href + '/' + str(page)
            self.img(page_url)  ##调用img函数

    def img(self, page_url):  ##这个函数处理图片页面地址获得图片的实际地址
        img_html = self.request(page_url)
        img_url = BeautifulSoup(img_html.text, 'lxml').find('div', class_='main-image').find('img')['src']
        self.save(img_url)

    def save(self, img_url):  ##这个函数保存图片
        name = img_url[-9:-4]
        img = self.request(img_url)
        f = open(name + '.jpg', 'ab')
        f.write(img.content)
        f.close()

    def mkdir(self, path):  ##这个函数创建文件夹
        path = path.strip()
        isExists = os.path.exists(os.path.join("/home/laomie/temp/mzitu", path))
        if not isExists:
            print(u'建了一个名字叫做', path, u'的文件夹！')
            os.makedirs(os.path.join("/home/laomie/temp/mzitu", path))
            return True
        else:
            print(u'名字叫做', path, u'的文件夹已经存在了！')
            return False

    def request(self, url):  ##这个函数获取网页的response 然后返回
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}
        # content.encoding需要和BeautifulSoup的'utf-8'一致，否则乱码
        content = requests.get(url, headers=headers)
        return content


en_book = BQGBook()  ##实例化
en_book.download('http://www.biquge.co')  ##给函数all_url传入参数  你可以当作启动爬虫（就是入口）