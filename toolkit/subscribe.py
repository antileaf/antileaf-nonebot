from tokenize import group
from . import database as db

from typing import *
import copy

'''
订阅系统应当有作者和用户两方面

作者：用一个字符串（名字）作为关键字，也可以存储一些附加信息
用户：分为个人用户和群聊用户，只需要一个整数存储 id 即可
'''

class Subscribe:
	def __init__(self, name):
		self.name = name

		self.database = db.Database('subscribe_' + name)

		self.database['authors'] = set()
		self.database['details'] = dict()
		self.database['sub_user'] = dict()
		self.database['sub_group'] = dict()

		self.authors = set()
		self.details = dict()
		self.sub_users = dict() # Dict[str, Set[int]]
		self.sub_groups = dict() # Dict[str, Set[int]]
	
	def load(self):
		self.database.fetch()

		self.authors = self.database['authors']
		self.details = self.database['details']
		self.sub_users = self.database['sub_user']
		self.sub_groups = self.database['sub_group']
	
	
	def add_author(self, author : str) -> bool:
		if author in self.authors:
			return False
		
		self.authors.add(author)
		self.details[author] = dict()
		self.sub_users[author] = set()
		self.sub_groups[author] = set()

		self.database.commit()

		return True
	
	def set_detail(self, author : str, detail : Dict[str, Any]) -> bool:
		if not author in self.authors:
			return False

		self.details[author] = copy.deepcopy(detail)

		self.database.commit()

		return True
	
	def update_detail(self, author : str, key : str, value : Any) -> bool:
		if not author in self.authors:
			return False
		
		self.details[author][key] = value

		self.database.commit()

		return True

	
	def del_author(self, author : str) -> bool:
		if not author in self.authors:
			return False
		
		self.authors.remove(author)
		del self.details[author]
		del self.sub_users[author]
		del self.sub_groups[author]
		
		self.database.commit()
		
		return True
	
	def check_author(self, author : str) -> bool:
		return author in self.authors

	
	# def add_user(self, user_id : int):
	# 	if not user_id in self.sub_user:
	# 		self.sub_user[user_id] = set()
	
	# def check_user(self, user_id : int):
	# 	return user_id in self.sub_user
	
	# def add_group(self, group_id : int):
	# 	if not group_id in self.sub_group:
	# 		self.sub_group[group_id] = set()
	
	# def check_group(self, group_id : int):
	# 	return group_id in self.sub_group

	
	def user_subscribe(self, user_id : int, author : str) -> int:
		if not self.check_author(author):
			return -1
		
		if user_id in self.sub_users[author]:
			return 0
		
		self.sub_users[author].add(user_id)

		self.database.commit()

		return 1
	
	def user_unsubscribe(self, user_id : int, author : str) -> int:
		if not self.check_author(author):
			return -1
		
		if not user_id in self.sub_users[author]:
			return 0
		
		self.sub_users[author].remove(user_id)

		self.database.commit()

		return 1
	
	def group_subscribe(self, group_id : int, author : str) -> int:
		if not self.check_author(author):
			return -1
		
		if group_id in self.sub_groups[author]:
			return 0
		
		self.sub_groups[author].add(group_id)

		self.database.commit()

		return 1
	
	def group_unsubscribe(self, group_id : int, author : str) -> int:
		if not self.check_author(author):
			return -1
		
		if not group_id in self.sub_groups[author]:
			return 0
		
		self.sub_users[author].remove(group_id)

		self.database.commit()

		return 1
		

	def get_authors(self) -> Set[str]:
		return self.authors

	def any_author(self) -> bool:
		return len(self.authors) > 0

	def get_detail(self, author : str) -> Dict[str, Any]:
		if not self.check_author(author):
			return dict()
		
		return self.details[author]
	
	def get_detail(self, author : str, key : str) -> Optional[Any]:
		if not self.check_author(author):
			return None
		
		if not key in self.details[author]:
			return None
		
		return self.details[author][key]
	
	def get_details(self, author : str, keys : Set[str]) -> Optional[Dict[str, Any]]:
		if not self.check_author(author):
			return None
		
		res = dict()

		for key in keys:
			if key in self.details[author]:
				res[key] = self.details[author][key]
		
		return res
	
	
	def get_subscribed_users(self, author : str) -> List[int]:
		if not self.check_author(author):
			return []
		
		return self.sub_users[author]
	
	def get_subscribed_groups(self, author : str) -> List[int]:
		if not self.check_author(author):
			return []
		
		return self.sub_groups[author]
	

	def get_user_subscribes(self, user_id : int) -> List[str]:
		subsc = []
		
		for author in self.authors:
			if user_id in author:
				subsc.append(author)
		
		return subsc
	
	def get_group_subscribes(self, group_id : int) -> List[str]:
		subsc = []

		for author in self.authors:
			if group_id in author:
				subsc.append(author)
		
		return subsc