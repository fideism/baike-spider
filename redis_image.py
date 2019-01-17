#coding:utf-8

import sys
import os
from urllib import request
import config
import redis
import time
import json
import common
import threading
import time

def getImage(redis_config):
    print(redis_config)
    host = redis_config.get('host')
    port = redis_config.get('port')
    db = redis_config.get('db')
    key = redis_config.get('key')
    redis_service = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    while True:
        saveImage(redis_service,host,key)
        time.sleep(1)
        pass

def saveImage(redis_service, host, key):
    image = redis_service.rpop(key)
    if image:
        print('服务器:%s, 获取图片信息:%s' % (host, image))
        image = json.loads(image)
        common.create_folder(image_dir + '/img/' + image['mainid'])
        downloadImage(image['filename'], image['url'])
    else:
        print('服务器:%s 图片数据为空' % host)

def downloadImage(filename, url):
    try:
        filename = image_dir + filename
        print(url)
        request.urlretrieve(url, filename)
        pass
    except Exception as e:
        print(e)

global image_dir
image_dir = config.image_dir
#创建文件夹
common.create_folder(image_dir + '/img')

threads = []

for config in config.redis_services:
    thread = threading.Thread(target=getImage, args=(config,))
    threads.append(thread)

for t in threads:
    t.setDaemon(True)
    t.start()

t.join()
