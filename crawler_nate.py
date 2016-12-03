# -*- coding: utf-8 -*-
import unicodedata
import urlparse
import urllib2
import re
import os
import sys
import time
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

        #self.start_date = infomation['start_date']
        #self.end_date = infomation['end_date']



    def __del__(self):
         pass

    # 기사 URL 크롤링

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def article_url_crawling(self):

        category_list = { 'baseball': '스포츠/야구', # Politic
                          'abrbaseball': '스포츠/해외야구',
                          'soccer': '스포츠/축구',
                          'abrsoccer': '스포츠/해외축구',
                          'basketvolley': '스포츠/농구배구',
                          'general': '스포츠/골프일반' }

        article = {}
        #for cat in category_list:
        #    make_sure_path_exists("D:/Development/DATA/Nate News 2015/"+cat)
        #

        start_date = date(2013, 6, 1)
        start_category = ''
        bStart = False

        end_date = date(2013, 10, 1)


        start_date_c = date(2012, 12, 6)
        end_date_c = date(2013, 1, 1)

        for single_date in self.daterange(start_date_c, end_date_c):
            for cat_id, cat_value in category_list.iteritems():
                cat_value = unicode(cat_value,'utf8')
                current_date = single_date.strftime("%Y%m%d")
                copyfile("D:/Development/DATA/Naver News 2012 2/"+cat_value+"/"+current_date+".txt","D:/Development/DATA/Naver News 2012/"+cat_value+"/"+current_date+".txt")

        sys.exit(0)





        for single_date in self.daterange(start_date, end_date):

            for cat_id, cat_value in category_list.iteritems():

                if start_category == cat_value or start_category == '' :
                    bStart = True
                elif bStart == False:
                    continue

                cat_value = unicode(cat_value,'utf8')

                current_date = single_date.strftime("%Y%m%d")
                current_url = self.start_url + cat_id + "/recent?type=t&date="+current_date
                print ''
                print cat_value + "-" + current_date + " : " + current_url

                f = codecs.open ("D:/Development/DATA/Naver News 2013/"+cat_value+"/"+current_date+".txt", "w", "utf-8")

                page_ct = 1
                page_max = 1
                ismax = False
                isnext = False

                while True:
                    sys.stdout.write('.')
                    try:
                        htmlText = urllib2.urlopen(current_url + "&page=" + str(page_ct)).read()
                    except:
                        print 'URL OPEN ERROR. (Sleep Mode ON... )'
                        time.sleep(60)
                        print 'Sleep Mode Off'
                        htmlText = urllib2.urlopen(current_url + "&page=" + str(page_ct)).read()

                    soup = BeautifulSoup(htmlText,"lxml")
                    soup2 = soup.find(id=self.list_contents_containner)

                    if soup2.find('p', class_="noData" ) is not None:
                        print "NoData"
                        break

                    for tag in soup.findAll('a', href = True):
                        tag['href'] = urlparse.urljoin(self.start_url, tag.get('href'))
                        article__url = [m.group(0) for m in re.finditer(self.uri_pattern, tag['href'])]
                        if len(article__url) != 0:
                            try:
                                htmlText = urllib2.urlopen(article__url[0]).read()
                            except:
                                print 'URL OPEN ERROR. (Sleep Mode ON... )'
                                time.sleep(60)
                                print 'Sleep Mode Off'
                                htmlText = urllib2.urlopen(article__url[0]).read()

                            soup_article = BeautifulSoup(htmlText,"lxml")

                            try:
                                article_title = soup_article.find(self.title_pattern['tag'], attrs=self.title_pattern['attrs']).text.strip()
                            except:
                                print 'Title Error-Cont'
                                continue;
                            #print article_title

                            article_content = soup_article.find(self.contents_pattern['tag'], attrs=self.contents_pattern['attrs'])

                            for remove_table in article_content.findAll('table', {"border" : "0"} ):
                                remove_table.extract()
                            for remove_table in article_content.findAll('caption'):
                                remove_table.extract()

                            for remove_tag in self.contents_pattern['remove_tags']:
                                for remove in article_content.findAll(remove_tag['tag'], attrs=remove_tag['attrs']):
                                    remove.extract()
                            # article['content'] = article['content'].text.strip()
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
                            f.write(content + "\r\n\r\n\r\n")
                            # print content

                    soup_page = soup2.find('div', id="paging" )
                    soup_next = soup_page.find('a', class_="next" )

                    if ismax == False:
                        ismax =True
                        if soup_next is not None:
                            page_max = page_ct + 9
                            isnext = True
                            # print page_max
                        else:
                            soup_page_max = soup_page.findAll('a', href=True )
                            if len(soup_page_max) == 0 or ( len(soup_page_max) == 1 and page_ct >= 11 ):
                                page_max = page_ct
                            else:
                                page_max_str = soup_page_max[-1].get_text()
                                page_max = int(page_max_str.strip())
                            # print page_max
                            isnext = False
                    if page_ct == page_max:
                        if isnext == True:
                            page_ct += 1
                            ismax = False
                        else:
                            break
                    else:
                        page_ct += 1
                f.close()

        '''
        for cat in category_list:
            start_date = date(2015, 1, 1)
            end_date = date(2015, 1, 3)
            for single_date in self.daterange(start_date, end_date):
                current_date = single_date.strftime("%Y%m%d")
                current_url = self.start_url + "&mid=" + cat + "&date="+current_date
                print cat + "-"+ current_date + " : " + current_url

                f = codecs.open ("D:/Development/DATA/Nate News 2015/"+cat+"/"+current_date+".txt", "w", "utf-8")

                htmlText = urllib2.urlopen(current_url).read()
                soup = BeautifulSoup(htmlText,"lxml")
                if self.list_contents_containner is not None:
                    soup = soup.find(id=self.list_contents_containner)
                #print soup
                for tag in soup.findAll('a', href = True):
                    tag['href'] = urlparse.urljoin(self.start_url, tag.get('href'))
                    article__url = [m.group(0) for m in re.finditer(self.uri_pattern, tag['href'])]
                    if len(article__url) != 0 and tag['href'] not in self.visited_urls:
                        self.visited_urls.append(tag['href'])
                        htmlText = urllib2.urlopen(tag['href']).read()
                        soup = BeautifulSoup(htmlText,"lxml")
                        article['title'] = soup.find(self.title_pattern['tag'], attrs=self.title_pattern['attrs']).text.strip()
                        if 'remove_tags' in self.contents_pattern:
                            article['content'] = soup.find(self.contents_pattern['tag'], attrs=self.contents_pattern['attrs'])
                            for remove_tag in self.contents_pattern['remove_tags']:
                                for remove in article['content'].findAll(remove_tag['tag'], attrs=remove_tag['attrs']):
                                    remove.extract()
                            article['content'] = article['content'].text.strip()
                        else:
                            article['content'] = soup.find(self.contents_pattern['tag'], attrs=self.contents_pattern['attrs']).text.strip()
                        #print article['title']
                        f.write(article['title'] + "\r\n\r\n")
                        content = re.sub( '\s+', ' ', article['content'] ).strip()
                        #print content
                        f.write(content + "\r\n\r\n\r\n")
        '''

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

            #기사 time 추출

            #
            #if 'sub_contents' in self.article_time_pattern:
            #    article['time'] = soup.find_all(self.article_time_pattern['tag'], attrs=self.article_time_pattern['attrs'])[0].find(self.article_time_pattern['sub_contents']['tag']).text.strip()
            #else:
            #    article['time'] = soup.find_all(self.article_time_pattern['tag'], attrs=self.article_time_pattern['attrs'])[0].text.strip()
            #print article['time']
            print article['title']
            content = re.sub( '\s+', ' ', article['content'] ).strip()
            print content

            #print '--1--'
            #print article['content'].replace('\n', ' ').replace('\t', ' ').strip()
            #hangul = re.compile('[^ \u3131-\u3163\uac00-\ud7a3]+')
            #content = hangul.sub('',article['content'])
            #article['content'] = re.compile('[^ \.\,\?\!a-zA-Z0-9\u3131-\u3163\uac00-\ud7a3]+')
            #content = article['content'].replace('[^\uAC00-\uD7A3xfe0-9a-zA-Z\\s.]',' ')
            #content = re.sub( '[^\u3131-\u3163\uac00-\ud7a30-9a-zA-Z\\s.]', ' ',  article['content'] ).strip()





            #print re.sub( '\s+', ' ', article['content'] ).strip()
            #print '--2--'

nate_sports = Crawler({
    'start_url' : 'http://sports.news.nate.com/',
    'uri_pattern' : 'http://sports.news.nate.com/view/.*\?mid=.*',
    'page_pattern' : '&page=2',
    'day_pattern' : '&date=20140717',
    'list_contents_containner' : 'cntArea',
    'title_pattern' : {
        'tag' : 'h3',
        'attrs' : {
            'class' : 'viewTite'
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
            }}, {
            'tag' : 'div',
            'attrs' : {
                'id' : 'newsmediaBanner'
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

nate_sports.article_url_crawling()


# nate_sports.article_parsing()

# nate_general.article_url_crawling()
# nate_general.article_parsing()
