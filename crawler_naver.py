# -*- coding: utf-8 -*-
import unicodedata
import urlparse
import urllib2
import sys
import time
import re
import os
import errno
import codecs
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from datetime import timedelta, date
from shutil import copyfile

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class Crawler:
    def __init__(self, infomation):
        # self.GuestID = id 
        self.start_url = infomation['start_url']
        self.uri_pattern = infomation['uri_pattern']
        self.day_pattern = infomation['day_pattern']
        self.page_pattern = infomation['page_pattern']
        self.list_contents_containner = infomation['list_contents_containner']
        self.title_pattern = infomation['title_pattern']
        self.contents_pattern = infomation['contents_pattern']
        self.article_time_pattern = infomation['article_time_pattern']

        self.urls = []
        self.visited_urls = []

        self.articles = []

        self.count_parsed_article = 0

        self.urls.append(self.start_url)
        self.visited_urls.append(self.start_url)

        # self.start_date = infomation['start_date']
        # self.end_date = infomation['end_date']


        
    def __del__(self):  
         pass

    # 기사 URL 크롤링

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def article_url_crawling(self):
        category_list = { 'mode=LS2D&mid=shm&sid1=100&sid2=264': '정치/청와대', # Politic
                          'mode=LS2D&mid=shm&sid1=100&sid2=265': '정치/국회정당',
                          'mode=LS2D&mid=shm&sid1=100&sid2=268': '정치/북한',
                          'mode=LS2D&mid=shm&sid1=100&sid2=266': '정치/행정',
                          'mode=LS2D&mid=shm&sid1=100&sid2=267': '정치/국방외교',
                          'mode=LS2D&mid=shm&sid1=100&sid2=269': '정치/정치일반',
                          'mode=LS2D&mid=shm&sid1=101&sid2=259': '경제/금융', # Economy
                          'mode=LS2D&mid=shm&sid1=101&sid2=258': '경제/증권',
                          'mode=LS2D&mid=shm&sid1=101&sid2=261': '경제/기업재계',
                          'mode=LS2D&mid=shm&sid1=101&sid2=260': '경제/부동산',
                          'mode=LS2D&mid=shm&sid1=101&sid2=262': '경제/글로벌경제',
                          'mode=LS2D&mid=shm&sid1=101&sid2=310': '경제/생활경제',
                          'mode=LS2D&mid=shm&sid1=101&sid2=263': '경제/경제일반',
                          'mode=LS2D&mid=shm&sid1=102&sid2=249': '사회/사건사고', # Society
                          'mode=LS2D&mid=shm&sid1=102&sid2=250': '사회/교육',
                          'mode=LS2D&mid=shm&sid1=102&sid2=251': '사회/노동',
                          'mode=LS2D&mid=shm&sid1=102&sid2=254': '사회/언론',
                          'mode=LS2D&mid=shm&sid1=102&sid2=252': '사회/환경',
                          'mode=LS2D&mid=shm&sid1=102&sid2=59b': '사회/인권복지',
                          'mode=LS2D&mid=shm&sid1=102&sid2=255': '사회/식품의료',
                          'mode=LS2D&mid=shm&sid1=102&sid2=256': '사회/지역',
                          'mode=LS2D&mid=shm&sid1=102&sid2=276': '사회/인물',
                          'mode=LS2D&mid=shm&sid1=102&sid2=257': '사회/사회일반',
                          'mode=LS2D&mid=shm&sid1=103&sid2=241': '생활문화/건강정보', # Culture
                          'mode=LS2D&mid=shm&sid1=103&sid2=239': '생활문화/자동차시승기',
                          'mode=LS2D&mid=shm&sid1=103&sid2=240': '생활문화/도로교통',
                          'mode=LS2D&mid=shm&sid1=103&sid2=237': '생활문화/여행레저',
                          'mode=LS2D&mid=shm&sid1=103&sid2=238': '생활문화/음식맛집',
                          'mode=LS2D&mid=shm&sid1=103&sid2=376': '생활문화/패션뷰티',
                          'mode=LS2D&mid=shm&sid1=103&sid2=242': '생활문화/공연전시',
                          'mode=LS2D&mid=shm&sid1=103&sid2=243': '생활문화/책',
                          'mode=LS2D&mid=shm&sid1=103&sid2=244': '생활문화/종교',
                          'mode=LS2D&mid=shm&sid1=103&sid2=248': '생활문화/날씨',
                          'mode=LS2D&mid=shm&sid1=103&sid2=245': '생활문화/생활문화일반',
                          'mode=LS2D&mid=shm&sid1=104&sid2=231': '세계/아시아호주', # World
                          'mode=LS2D&mid=shm&sid1=104&sid2=232': '세계/미국중남미',
                          'mode=LS2D&mid=shm&sid1=104&sid2=233': '세계/유럽',
                          'mode=LS2D&mid=shm&sid1=104&sid2=234': '세계/중동아프리카',
                          'mode=LS2D&mid=shm&sid1=104&sid2=322': '세계/세계일반',
                          'mode=LS2D&mid=shm&sid1=105&sid2=731': 'IT과학/모바일', # IT
                          'mode=LS2D&mid=shm&sid1=105&sid2=226': 'IT과학/인터넷SNS',
                          'mode=LS2D&mid=shm&sid1=105&sid2=227': 'IT과학/통신뉴미디어',
                          'mode=LS2D&mid=shm&sid1=105&sid2=230': 'IT과학/IT일반',
                          'mode=LS2D&mid=shm&sid1=105&sid2=732': 'IT과학/보안해킹',
                          'mode=LS2D&mid=shm&sid1=105&sid2=283': 'IT과학/컴퓨터',
                          'mode=LS2D&mid=shm&sid1=105&sid2=229': 'IT과학/게임리뷰',
                          'mode=LS2D&mid=shm&sid1=105&sid2=228': 'IT과학/과학일반',
                          'mode=LS2D&mid=shm&sid1=106&sid2=221': '연예/연예가화제', # Entertainment
                          'mode=LS2D&mid=shm&sid1=106&sid2=224': '연예/방송TV',
                          'mode=LS2D&mid=shm&sid1=106&sid2=225': '연예/드라마',
                          'mode=LS2D&mid=shm&sid1=106&sid2=222': '연예/영화',
                          'mode=LS2D&mid=shm&sid1=106&sid2=309': '연예/해외연예' }

        start_date = date(2012, 12, 15)
        start_category = ''
        # start_page = '경제/기업재계'
        bStart = False

        end_date = date(2012, 12, 17)



        start_date_c = date(2012, 12, 6)
        end_date_c = date(2012, 12, 15)

        for single_date in self.daterange(start_date_c, end_date_c):
            for cat_id, cat_value in category_list.iteritems():
                cat_value = unicode(cat_value,'utf8')
                current_date = single_date.strftime("%Y%m%d")
                copyfile("D:/Development/DATA/Naver News 2012 2/"+cat_value+"/"+current_date+".txt","D:/Development/DATA/Naver News 2012/"+cat_value+"/"+current_date+".txt")

        sys.exit(0)


        for single_date in self.daterange(start_date, end_date):

            for cat_id, cat_value in category_list.iteritems():
                # start_date = date(2013, 1, 2)
                # end_date = date(2013, 12, 31)
                if start_category == cat_value or start_category == '' :
                    bStart = True
                elif bStart == False:
                    continue

                cat_value = unicode(cat_value,'utf8')

                # for single_date in self.daterange(start_date, end_date):

                current_date = single_date.strftime("%Y%m%d")
                current_url = self.start_url + cat_id + "&date="+current_date
                print ''
                print cat_value + "-" + current_date + " : " + current_url

                # cat_value = unicode(cat_value,'utf8')
                # cat_value = cat_value.encode('utf8')

                article_url_set = set()
                f = codecs.open ("D:/Development/DATA/Naver News 2012/"+cat_value+"/"+current_date+".txt", "w", "utf-8")

                try:
                    htmlText = urllib2.urlopen(current_url + "&page=1000").read()
                except:
                    print 'URL OPEN ERROR. (Sleep Mode ON... )'
                    time.sleep(60)
                    print 'Sleep Mode Off'
                    htmlText = urllib2.urlopen(current_url + "&page=1000").read()

                soup = BeautifulSoup(htmlText,"lxml")
                paging_content = soup.find('div', class_="paging")
                paging_content = paging_content.find('strong')

                max_page = str(paging_content.get_text())

                # print 'max_page : ' + str(paging_content.get_text())
                sys.stdout.write(max_page + ' ')
                for article_page_no in range(1, int(max_page)+1 ):
                    #print article_page_no
                    sys.stdout.write('.')
                    try:
                        htmlText = urllib2.urlopen(current_url + "&page=" + str(article_page_no)).read()
                    except:
                        print 'URL OPEN ERROR. (Sleep Mode ON... )'
                        time.sleep(60)
                        print 'Sleep Mode Off'
                        htmlText = urllib2.urlopen(current_url + "&page=" + str(article_page_no)).read()

                    soup = BeautifulSoup(htmlText,"lxml")

                    # if self.list_contents_containner is not None:
                    soup = soup.find(id=self.list_contents_containner)

                    for remove_photo in soup.findAll('dt', class_= "photo"):
                        remove_photo.extract()

                    for tag in soup.findAll('a', href = True):
                        #tag['href'] = urlparse.urljoin(self.start_url, tag.get('href'))
                        article_url = tag.get('href')
                        if article_url.startswith ('http'):
                            #f.write(tag['href'] + "\r\n")
                            # print article_url

                            try:
                                htmlText_article = urllib2.urlopen(article_url).read()
                            except:
                                print 'URL OPEN ERROR. (Sleep Mode ON... )'
                                time.sleep(60)
                                print 'Sleep Mode Off'
                                htmlText_article = urllib2.urlopen(article_url).read()

                            soup_article = BeautifulSoup(htmlText_article,"lxml")

                            soup_article_content = soup_article.find('div', class_="end_ct_area")
                            soup_article_content2 = soup_article.find('div', id="main_content")

                            if soup_article_content is not None:
                                article_title = soup_article_content.find('p', class_="end_tit").text.strip()
                                article_content = soup_article_content.find('div', id="articeBody")
                                for remove_tag in self.contents_pattern['remove_tags']:
                                    for remove in article_content.findAll(remove_tag['tag'], attrs=remove_tag['attrs']):
                                        remove.extract()
                                # print "TITLE : " + article_title
                                f.write(article_title + "\r\n\r\n")
                                text = [i for i in article_content.recursiveChildGenerator() if type(i) == NavigableString]
                                bPunc = False
                                text_str = ""
                                for element in reversed(text):
                                    element = element.strip()
                                    if (element.endswith(".") and bPunc==False) or bPunc==True:
                                        bPunc = True
                                        text_str = " " + element.strip() + text_str
                                content = text_str.strip()
                                content = re.sub( '\s+', ' ', content ).strip()
                                # print "Content : " + content
                                f.write(content + "\r\n\r\n\r\n")
                            elif soup_article_content2 is not None:
                                article_title = soup_article_content2.find('h3', id="articleTitle").text.strip()
                                article_content = soup_article_content2.find('div', id="articleBodyContents")
                                for remove_tag in self.contents_pattern['remove_tags']:
                                    for remove in article_content.findAll(remove_tag['tag'], attrs=remove_tag['attrs']):
                                        remove.extract()
                                # print "TITLE : " + article_title
                                f.write(article_title + "\r\n\r\n")
                                text = [i for i in article_content.recursiveChildGenerator() if type(i) == NavigableString]
                                bPunc = False
                                text_str = ""
                                for element in reversed(text):
                                    element = element.strip()
                                    if (element.endswith(".") and bPunc==False) or bPunc==True:
                                        bPunc = True
                                        text_str = " " + element.strip() + text_str
                                content = text_str.strip()
                                content = re.sub( '\s+', ' ', content ).strip()
                                # print "Content : " + content
                                f.write(content + "\r\n\r\n\r\n")
                f.close()

    def rowparser(row):
        row = row.replace('"', '').replace("\\n","").replace("\\N","").replace("'", '').replace("[","").replace("]","")
        return row


    # 기사 내용 파싱 
    def article_parsing(self):
        article = {}
        for index in range(self.count_parsed_article + 1, len(self.visited_urls)):
            print self.visited_urls[index]


            htmlText = urllib2.urlopen(self.visited_urls[index]).read()
           
            soup = BeautifulSoup(htmlText,"lxml")


            article['title'] = soup.find(self.title_pattern['tag'], attrs=self.title_pattern['attrs']).text.strip()
            #print article['title']

            #기사 content에 제거할 element가 있으면 제거 
            if 'remove_tags' in self.contents_pattern:
                article['content'] = soup.find(self.contents_pattern['tag'], attrs=self.contents_pattern['attrs'])
                for remove_tag in self.contents_pattern['remove_tags']:
                    for remove in article['content'].findAll(remove_tag['tag'], attrs=remove_tag['attrs']):
                        remove.extract()
                article['content'] = article['content'].text.strip()
            else:
                article['content'] = soup.find(self.contents_pattern['tag'], attrs=self.contents_pattern['attrs']).text.strip()    


            print article['title']
            content = re.sub( '\s+', ' ', article['content'] ).strip()
            print content


naver_general = Crawler({
    'start_url' : 'http://news.naver.com/main/list.nhn?',
    'uri_pattern' : 'http://news.nate.com/view/.*\?mid=.*',
    'page_pattern' : '&page=2',
    'day_pattern' : '&date=20140717',
    'list_contents_containner' : 'main_content',
    'title_pattern' : {
        'tag' : 'h3',
        'attrs' : {
            'class' : 'articleSubecjt'
        }
    },
    'contents_pattern' : {
        'tag' : 'div',
        'attrs' : {
            'id' : 'articleContetns'
        },
        'remove_tags' : [{
            'tag' : 'script',
            'attrs' : {
            }}
        ]
    },
    'article_time_pattern' : {
        'tag' : 'dl',
        'attrs' : {
            'class' : 'articleInfo' # need
        },
        'sub_contents' : {
            'tag' : 'em',
        }
    }

})

naver_general.article_url_crawling()
