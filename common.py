#coding:utf-8

import os
import hashlib

def str_encrypt(str):
    """
    使用sha1加密算法，返回str加密后的字符串
    """
    hash = hashlib.sha1()
    hash.update(str.encode('utf-8'))
    encrypts = hash.hexdigest()
    return encrypts

def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

def parse_image_url(mainid, url):
    image_name = '/img/%s/%s.%s' % (mainid, str_encrypt(url), url.split('.')[-1])
    #image_name = '/%s/%s.%s' % (mainid, str_encrypt(url), url.split('.')[-1])
    return image_name

# 生成唯一编号
# docIds = {
#     'mainid' : main_dict['lemmaId'],
#     'subid' : main_dict['subLemmaId'],
#     'newLemmaId' : main_dict['newLemmaId']
# }
def getUniqueId(docIds):
    #TODO
    return docIds['mainid']
