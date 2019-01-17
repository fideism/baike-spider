#coding:utf-8

import os
import sys
import re

path = '/data/www/baike_sql'
sql_file = '%s/baike.sql' % path
sql_file = open(sql_file, mode='a+', encoding='UTF-8')

def readDir(path):
	pathDir = os.listdir(path)

	for item in pathDir:
		new = '%s/%s' % (path, item)
		if os.path.isfile(new):
			sql = 'source %s;' % new
			sql_file.writelines(sql + '\n')
			print(sql)
		else:
			readDir(new)

readDir(path)
sql_file.close()
