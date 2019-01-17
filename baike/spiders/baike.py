# coding:utf-8

import sys
import os
import json
import scrapy
from bs4 import BeautifulSoup
from ..items import BaikeItem
from scrapy import log
import time
import common
from urllib.parse import urlparse
import config

# split -l 2482 BLM.txt -d -a 4 BLM_

class BaikeSpider(scrapy.Spider):
    name = 'baike'
    #allowed_domains = ['baike.baidu.com']

    def start_requests(self):
        page_file = open(config.pages_file, mode='r+', encoding='UTF-8')
        page_list = [str(page).strip() for page in page_file]
        page_file.close()
        for page in range(config.start, config.end):
            if (str(page) in page_list):
                print('ignore page:%d' % page)
                continue
            else:
                url = 'https://baike.baidu.com/view/%d.html' % page
                print('请求url:%s' % url)
                yield scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'page': page})
        # url = 'https://baike.baidu.com/item/%E7%8E%9B%E4%B8%BD%E4%BA%9A%C2%B7%E5%8D%A1%E6%8B%89%E6%96%AF'
        # yield scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'page':11})

    def parse(self, response):
        # 错误页面
        request_url = 'https://baike.baidu.com/view/%d.html' % response.meta['page']
        if (common.str_encrypt(response.url) == common.str_encrypt('https://baike.baidu.com/error.html')):
            log.msg('请求页面错误，request url:%s,  return error html' %request_url, level=log.ERROR)
            return

        try:
            content = BeautifulSoup(response.body, "html.parser")

            # 同义词处理
            lemmaWgt = content.select('div[class="lemmaWgt-subLemmaListTitle"]')
            if (len(lemmaWgt)):
                words = content.select('li[class="list-dot list-dot-paddingleft"]')
                if (len(words)):
                    print(words)
                    for word in words:
                        url = 'https://baike.baidu.com%s' % word.find('a')['href']
                        print('同义词处理，返回url:%s, 请求url:%s' % (response.url, url))
                        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={'page': response.meta['page']})
                    return

            # 其他情况处理
            main_item = response.xpath('//script').re("nslog\(\)\.setGlobal\(\{([\d\D]*?)\}\)")[0]
            main_dict = self.__getMainDict(main_item)
            # for data in main_item.split(','):
            #     (key, value) = self.__parseData(data)
            #     main_dict[key] = value
            #{'lemmaId': '1719', 'newLemmaId': '16191846', 'subLemmaId': '16136678', 'lemmaTitle': '曹操'}

            main_dict['desc'] = content.find(attrs={"name": "description"})['content']

            title_item = content.find('title').string.rstrip('）_百度百科').split('（')
            main_dict['title'] = title_item[0]
            main_dict['item'] = title_item[1] if len(title_item) >= 2 else ''
            #{'title': '曹操', 'newLemmaId': '16191846', 'subLemmaId': '16136678', 'item': '游戏《英雄三国》角色', 'desc': '曹操是一位远程输出型英雄，能够无视敌人的 部分防御，同时拥有强大的远程输出能力。英雄定位： 双修,爆发,后期 远程 老手...', 'lemmaId': '1719', 'lemmaTitle': '曹操'}
            # 主体内容
            wrapper = content.select('div[class="content-wrapper"]')[0]
            wrapper = self.__delWrapper(wrapper)

            # 图片、链接处理
            docIds = {
                'mainid' : main_dict['lemmaId'],
                'subid' : main_dict['subLemmaId'],
                'newLemmaId' : main_dict['newLemmaId']
            }
            (image_urls, wrapper) = self.__parseWrapper(wrapper, common.getUniqueId(docIds))

            relates = content.select('div[class="polysemant-list polysemant-list-normal"]')
            relates = self.__parseRelate(relates)

            data = BaikeItem()
            data['page'] = str(response.meta['page'])
            data['item'] = main_dict['title']
            data['title'] = main_dict['item']
            data['description'] = main_dict['desc']
            data['mainid'] = main_dict['lemmaId']
            data['subid'] = main_dict['subLemmaId']
            data['newLemmaId'] = main_dict['newLemmaId']
            data['content_wrapper'] = wrapper
            data['tags'] = self.__parseSpan(content.select('span[class="taglist"]'))
            data['sort_order'] = 0
            data['time'] = int(time.time())
            data['images'] = image_urls
            data['relates'] = relates
            yield data

        except Exception as e:
            self.parseException(request_url)
        except:
            self.parseException(request_url)

    def parseException(self, request_url):
        """deal exception"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'type': exc_type.__name__,
            'message': exc_value
        }
        print(traceback_details)
        message = 'request_url:%s, message:%s' % (request_url, traceback_details['message'])
        log.msg(message, level=log.ERROR)
        #错误URL
        error_file = open(config.error_file, mode='a+', encoding='UTF-8')
        error_file.writelines(request_url + '\n')
        error_file.close()

    def json_encode(self, items):
        """ json encode charset """
        return json.dumps(items, ensure_ascii=False)

    def __parseWrapper(self, wrapper, uniqueId):
        # 处理图片
        image_urls = []
        for image in wrapper.select('img'):
            attrs = image.attrs
            if ('data-src' in attrs.keys()):
                url = image['data-src']
            elif ('src' in attrs.keys()):
                url = image['src']
            else:
                continue

            filename = common.parse_image_url(uniqueId, url)
            image_urls.append({
                'filename': filename,
                'url': url,
                'mainid': uniqueId
            })
            image['src'] = filename
            del image['data-src']

        # 页面内部
        for item in wrapper.select('div[class="lemma-picture text-pic layout-right"]'):
            item.a['href'] = 'javascript:void(0)'
            del item.img['data-src']

        # 右侧
        for item in wrapper.select('div[class="summary-pic"]'):
            item.a['href'] = 'javascript:void(0)'
            del item.img['data-src']

        return image_urls, str(wrapper).replace('\n', '').replace('\r\n', '')

    def __delWrapper(self, wrapper):
        for item in wrapper.select('div[class="album-list"]'):
            item.decompose()

        for item in wrapper.select('div[class="mod-detailtable"]'):
            item.decompose()

        for item in wrapper.select('div[class="configModuleBanner"]'):
            item.decompose()

        for item in wrapper.find_all('div', id='hotspotmining_s'):
            item.decompose()

        for item in wrapper.select('div[class="tashuo-bottom"]'):
            item.decompose()

        for item in wrapper.select('div[class="tashuo-right"]'):
            item.decompose()

        for item in wrapper.select('div[class="lemmaWgt-promotion-vbaike"]'):
            item.decompose()

        for item in wrapper.select('div[class="lemmaWgt-sideRecommend"]'):
            item.decompose()

        for item in wrapper.select('div[class="zhixin-group js-group"]'):
            item.decompose()

        for item in wrapper.select('div[class="lemmaWgt-promotion-slide"]'):
            item.decompose()

        return wrapper

    def __parseRelate(self, relates):
        items = []
        for item in relates:
            for li in item.select('li'):
                if (li.a):
                    href = urlparse(li.a['href'])
                    title = li.a['title']
                    items.append({
                        'item': title,
                        'newLemmaId': href.path.split('/')[-1]
                    })
                    pass
                pass
            pass

        return items

    def __parseSpan(self, data):
        span_list = []
        for item in data:
            span_list.append(item.text.strip())
        return ','.join(span_list)

    def __parseData(self, data):
        temp = data.strip().split(':')
        key = temp[0].strip()
        value = temp[1].strip().strip('"')
        return key, value

    def __getMainDict(select, items):
        '''
            某些标题中带有逗号，特殊处理
        '''
        items_list = items.split()
        items_dict = {}
        items_list_len = int(len(items_list) / 2)
        for index in range(0, items_list_len):
            index = index * 2
            key = items_list[index].strip().strip(',').strip(':').strip('"')
            value = items_list[index + 1].strip().strip(',').strip(':').strip('"')
            items_dict[key] = value
        return items_dict
