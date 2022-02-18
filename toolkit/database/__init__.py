# -*- coding: utf-8 -*-

import nonebot
from nonebot import on_command, CommandSession, message
from nonebot import permission as perm
from nonebot.message import MessageSegment as ms

from nonebot.plugin import on_plugin


from typing import *
import os, copy

from . import pickle as pk


class Database:
	def __init__(self, name, default = dict()):
		self.name = name
		self.default = copy.deepcopy(default)

		self.tbl = dict()
	
	def __contains__(self, key):
		return key in self.tbl

	def __getitem__(self, key):
		if not key in self.tbl:
			self.tbl = copy.deepcopy(self.default)
		
		return self.tbl[key]
	
	def __setitem__(self, key, value):
		self.tbl[key] = value
	
	def __delitem__(self, key):
		if key in self.tbl:
			del self.tbl[key]
	
	def fetch(self):
		temp = pk.load(self.name)

		if temp:
			self.tbl = copy.deepcopy(temp)

	def commit(self):
		pk.save(self.name, self.tbl)


database = dict() # Dict[str, Database]


@on_plugin('loading')
def load_all():
	global database

	for file in os.listdir('data'):
		if file.endswith('.pk'):
			name = file[:-3]

			database[name] = pk.load(name)


def get(name : str, default = dict()):
	'''
	获取某个数据库
	'''

	global database

	if not name in database:
		database[name] = Database(name, default)

	return database[name]