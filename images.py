#coding:utf-8
import sys
import os
from urllib import request
import config
import redis
import time
import json
import common

class Images(object):
	def __init__(self):
		self.redis = redis.Redis(host=config.redis_host, port=config.redis_port, db=config.redis_db, decode_responses=True)
		pass

	def run(self):
		common.create_folder(config.image_dir + '/img')

		while True:
			image = self.redis.rpop('images')
			if image:
				image = json.loads(image)
				print(image)
				common.create_folder(config.image_dir + '/img/' + image['mainid'])
				#common.create_folder(config.image_dir + '/' + image['mainid'])

				self.__saveImage(image['filename'], image['url'])
				time.sleep(0.5)
			else:
				time.sleep(10)
			pass

	def __saveImage(self, filename, url):
		try:
			filename = config.image_dir + filename
			print(filename)
			print(url)
			request.urlretrieve(url, filename)
			pass
		except Exception as e:
			print(e)

image = Images()
image.run()
