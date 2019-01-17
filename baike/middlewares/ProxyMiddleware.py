#coding:utf-8

import redis
import json
import telnetlib

class ProxyMiddleware(object):

    def __init__(self):
        self.redis = redis.Redis(host='127.0.0.1', port=6379, db=0)

    def process_request(self, request, spider):
        proxy = self.__get_ip()
        url = "%s://%s:%s" % (proxy['http'].lower(),proxy['ip'], proxy['port'])
        request.meta['proxy'] = url
        request.meta['download_timeout'] = 60
        print(request.meta)
        print(request.headers)

    def __get_ip(self):
        while True:
            data = json.loads(self.redis.lpop('baike_ips').decode())
            if (self.__check(data['ip'], data['port'])):
                print('valid data %s' % data)
                #有效IP重新 放入redis使用
                self.redis.rpush('baike_ips', json.dumps(dict(data)))
                break
            else:
                print('invalid data %s' % data)

        return data


    def __check(self,ip, port):
        try:
            telnetlib.Telnet(ip, port=port, timeout=10)
        except:
            return False
        else:
            return True
