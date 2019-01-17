# coding:utf-8
import sys
import os
import scrapy
from bs4 import BeautifulSoup


class HycSpider(scrapy.Spider):
    name = 'hyc'
    #allowed_domains = ['baike.baidu.com']

    def start_requests(self):
        urls = [
            'https://baike.baidu.com/view/657071.html',
            'https://baike.baidu.com/item/%E4%B8%80%E5%8F%B6%E8%90%BD'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        content = BeautifulSoup(response.body, "html.parser")
        lemmaWgt = content.select('div[class="lemmaWgt-subLemmaListTitle"]')
        if (len(lemmaWgt)):
            words = content.select('li[class="list-dot list-dot-paddingleft"]')
            if (len(words)):
                for word in words:
                    url = 'https://baike.baidu.com%s' % word.find('a')['href']
                    print(url)
            else:
                print('aaa')
            return
        print('bbb')
