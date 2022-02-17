import pickle

from typing import *

from .parser import Blog, Article, get_blog

pk_file = 'temp/rss.pk'

rss_tbl = dict() # dict[name : str, url : str]
blog_tbl = dict() # dict[name : str, Blog]
sub_users = dict() # dict[name : str, list[user_id : int]]
sub_groups = dict()


def save_all():
	with open(pk_file, 'wb') as f:
		pickle.dump((rss_tbl, blog_tbl, sub_users, sub_groups), f)

def load_all():
	global rss_tbl, blog_tbl, sub_users, sub_groups

	try:
		with open(pk_file, 'rb') as f:
			rss_tbl, blog_tbl, sub_users, sub_groups = pickle.load(f)

	except:
		rss_tbl, sub_users, sub_groups = dict(), dict(), dict()


def add_rss(author : str, feed_url : str):
	global rss_tbl, blog_tbl, sub_users, sub_groups

	if author in rss_tbl:
		return False

	rss_tbl[author] = feed_url
	blog_tbl[author] = get_blog(feed_url)
	sub_users[author] = []
	sub_groups[author] = []

	save_all()

	return True

def del_rss(author : str): # 只向用户通知
	global rss_tbl, sub_users, sub_groups

	if not author in rss_tbl:
		return []
	
	del rss_tbl[author]
	bak = sub_users[author][:]

	del blog_tbl[author]
	del sub_users[author]
	del sub_groups[author]

	save_all()

	return bak


def add_user(user_id : int, author : str):
	global sub_users

	if user_id in sub_users[author]:
		return False
	
	sub_users[author].append(user_id)
	
	save_all()

	return True

def del_user(user_id : int, author : str):
	global sub_users

	if not user_id in sub_users[author]:
		return False
	
	sub_users[author].remove(user_id)

	save_all()

	return True

def add_group(group_id : int, author : str):
	global sub_groups

	if group_id in sub_groups[author]:
		return False
	
	sub_groups[author].append(group_id)

	save_all()

	return True

def del_group(group_id : int, author : str):
	global sub_groups

	if not group_id in sub_groups[author]:
		return False
	
	sub_groups[author].remove(group_id)

	save_all()

	return True


def check_author(author : str):
	return author in rss_tbl

def get_feed_url(author : str):
	return rss_tbl[author]

def get_rss_tbl():
	return dict(rss_tbl)


def query_users(author : str):
	return sub_users[author]

def query_groups(author : str):
	return sub_groups[author]


def query_author_by_user(user_id : int):
	a = []

	for o in rss_tbl:
		if user_id in sub_users[o]:
			a.append(o)
	
	return a

def query_author_by_group(group_id : int):
	a = []

	for o in rss_tbl:
		if group_id in sub_groups[o]:
			a.append(o)
	
	return a


def update_blog_info(author : str):
	global blog_tbl

	blog_tbl[author] = get_blog(rss_tbl[author])

	save_all()

def update_all():
	global blog_tbl

	for author in rss_tbl:
		blog_tbl[author] = get_blog(rss_tbl[author])
	
	save_all()

def query_blog(author : str) -> Optional[Blog]:
	if not check_author(author):
		return None
	
	return blog_tbl[author]

def get_blog_url(author : str):
	return blog_tbl[author].link