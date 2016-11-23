from bs4 import BeautifulSoup

class YoutubedLink():
    def print_links(self, file: str) :
        li_class = 'yt-uix-scroller-scroll-unit '

        with open(file, encoding="utf8") as contents:
            all_li = BeautifulSoup(contents, 'html.parser').find_all('li', class_=li_class)

            for li in all_li:
                if li is not None:
                    #print(li.get('data-video-title'))
                    a = li.find('a')
                    if a is not None:
                        print(a.get('href'))


youtube = YoutubedLink()
youtube.print_links('/home/laomie/Documents/test.html')