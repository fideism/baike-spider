# -*- coding: utf-8 -*-

from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class AgentMiddleware(UserAgentMiddleware):
    def __init__(self, agents):
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random
        request.headers['Host'] = 'baike.baidu.com'
        request.headers['Cache-Control'] = 'max-age=0'
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        request.headers['Upgrade-Insecure-Requests'] = 1
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'