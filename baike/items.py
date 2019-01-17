# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class BaikeItem(scrapy.Item):
    item = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    mainid = scrapy.Field()
    subid = scrapy.Field()
    newLemmaId = scrapy.Field()
    content_wrapper = scrapy.Field()
    time = scrapy.Field()
    tags = scrapy.Field()
    sort_order = scrapy.Field()
    images = scrapy.Field()
    relates = scrapy.Field()
    page = scrapy.Field()
    pass
