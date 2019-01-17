# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy import Request
import common
import pymysql
import config
import redis
import json

class BaikePipeline(object):
    def __init__(self):
        self.redis = redis.Redis(host=config.redis_host, port=config.redis_port, db=config.redis_db, decode_responses=True)
        pass

    def process_item(self, item, spider):
        data = item
        #异步redis处理图片
        self.__saveImages(data['images'])
        del data['images']

        self.__sql(data)
        return item

    def __saveImages(self, images):
        for image in images:
            self.redis.lpush(config.redis_key, json.dumps(dict(image)))

    def __sql(self, data):
        page = str(data['page'])
        del data['page']
        #保存已抓取页码
        page_file = open(config.pages_file, mode='a+', encoding='UTF-8')
        page_file.writelines(page + '\n')
        page_file.close()

        relates = data['relates']
        del data['relates']
        
        if (config.mdx_flag) : 
            content_file = open(config.content_file, mode='a+', encoding='UTF-8')
            content_file.writelines(data['wrapper'] + '\n')
            content_file.close()

        data = self.__parseData(data)

        #doc
        filename = config.doc_file % (int(page) % 100)
        doc_file = open(filename, mode='a+', encoding='UTF-8')
        doc_table = 'pf_sphinx_docs'
        sql = self.__genSql(data, doc_table)
        doc_file.writelines(sql + ';\n')

        #lemma
        lemma = {
            'word' : data['item'],
            'created_at' : data['time'],
            'updated_at' : data['time']
        }
        lemma_table = 'pf_sphinx_lemma'
        sql = self.__genSql(lemma, lemma_table)
        doc_file.writelines(sql + ';\n')
        doc_file.close()

        #同义词
        synonym_table = 'pf_sphinx_synonym'
        synonym_relate_table = 'pf_sphinx_synonym_relate'

        #同义词 新增
        if (len(relates) > 0) :
            relate_file = open(config.relate_file, mode='a+', encoding='UTF-8')
            synonym = {
                'id' : data['newLemmaId'],
                'item' : data['item'],
                'type' : 0,
                'created_at' : data['time']
            }
            # sql = "DELETE FROM `%s` where `syn_id` in (SELECT id FROM `%s` where `item` = '%s')" % ('pf_sphinx_synonym_relate', 'pf_sphinx_synonym', synonym['item'])
            # relate_file.writelines(sql + ';\n')
            # sql = "DELETE FROM `%s` where `item` = '%s'" % ('pf_sphinx_synonym', synonym['item'])
            # relate_file.writelines(sql + ';\n')
            sql = self.__genSql(synonym, synonym_table)
            relate_file.writelines(sql + ';\n')
            for relate in relates:
                data = {
                    'syn_id' : synonym['id'],
                    'item' : relate['item'],
                    'title' : relate['item'],
                    'newLemmaId' : relate['newLemmaId']
                }
                sql = self.__genSql(data, synonym_relate_table)
                relate_file.writelines(sql + ';\n')

    def __genSql(self, data, table):
        sql = "REPLACE INTO `%s`(`%s`) VALUES('%s')" % (table, '`,`'.join(data.keys()), "','".join(map(str, data.values())))
        return sql

    def __parseData(self, data):
        data['content_wrapper'] = pymysql.escape_string(data['content_wrapper'])
        data['description'] = pymysql.escape_string(data['description'])
        data['item'] = pymysql.escape_string(data['item'])
        data['title'] = pymysql.escape_string(data['title'])
        return data


class DownloadImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):  # 下载图片
        for image_url in item['images']:
            yield Request(image_url, meta={'mainid': item['mainid']})  # 添加meta是为了下面重命名文件名使用

    def file_path(self, request, response=None, info=None):
        url = request.url
        mainid = request.meta['mainid']
        return common.parse_image_url(mainid, url)

