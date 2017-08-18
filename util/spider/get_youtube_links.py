from bs4 import BeautifulSoup

class YoutubedLink():
    def print_links(self, file: str) :
        '''
        li_class = 'yt-lockup-title '

        with open(file, encoding="utf8") as contents:
            all_h3 = BeautifulSoup(contents, 'html.parser').find_all('h3', class_=li_class)

            for h3 in all_h3:
                if h3 is not None:
                    #print(li.get('data-video-title'))
                    a = h3.find('a')
                    if a is not None:
                        print(a.get('href'))
        '''
        with open(file, encoding="utf8") as contents:
            all_a = BeautifulSoup(contents, 'html.parser').find_all('a')

            for a in all_a:
                if a is not None:
                    link = str(a.get('href'))
                    if link.endswith('pdf') or link.endswith('ipynb'):
                        print('http://www.cs.toronto.edu/~rgrosse/courses/csc321_2017/' + link)


youtube = YoutubedLink()
youtube.print_links('/home/laomie/Documents/test.html')