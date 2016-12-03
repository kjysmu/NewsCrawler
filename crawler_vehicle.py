# -*- coding: utf-8 -*-
import unicodedata
import urlparse
import urllib2
import re
import os
import errno
import codecs
from bs4 import BeautifulSoup
from datetime import timedelta, date

hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'
       }

hdr2 = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'
       }


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

class Crawler:
    def __init__(self, infomation):
        self.start_url = infomation['start_url']

    def __del__(self):  
         pass

    def article_crawling(self):
        year_list = ['2016']

        for year in year_list:
            f = codecs.open ("F:/vc_dataset/"+year+".txt", "w", "utf-8")
            for article_page in range(0,99):

                current_url = self.start_url + "&as_ylo=" + year + "&start="+str(article_page*10)
                print current_url

                req = urllib2.Request(current_url, headers=hdr)
                htmlText = urllib2.urlopen(req).read()

                soup = BeautifulSoup(htmlText,"lxml")

                for article in soup.find_all('div', class_="gs_ri"):
                    title = article.find('h3', class_="gs_rt")
                    if title is not None:
                        title = title.find('a', href=True)
                        if title is not None:
                            title = title.get_text()
                            print "TITLE : " + title + "\n"
                            f.write(title + "\r\n\r\n")
                            abstract = article.find('div', class_="gs_rs")
                            if abstract is not None:
                                abstract = abstract.get_text()
                                abstract = re.sub( '\s+', ' ', abstract ).strip()
                                print "ABSTRACT : " + abstract + "\n"
                                f.write(abstract + "\r\n\r\n\r\n")

vehicle_collision = Crawler({
    'start_url' : 'http://scholar.google.com/scholar?as_sdt=0,5&hl=en&q=vehicle+collision',

})

vehicle_collision.article_crawling()
