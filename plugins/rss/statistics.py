import pickle

pk_file = 'temp/rss.pk'

rss_tbl = dict() # dict[name : str, url : str]
sub_users = dict() # dict[name : str, list[user_id : int]]
sub_groups = dict()


def save_all():
	with open(pk_file, 'wb') as f:
		pickle.dump((rss_tbl, sub_users, sub_groups), f)

def load_all():
	global rss_tbl, sub_users, sub_groups

	try:
		with open(pk_file, 'rb') as f:
			rss_tbl, sub_users, sub_groups = pickle.load(f)

	except:
		rss_tbl, sub_users, sub_groups = dict(), dict(), dict()


def add_rss(name : str, url : str):
	global rss_tbl, sub_users, sub_groups

	if name in rss_tbl:
		return False

	rss_tbl[name] = url
	sub_users[name] = []
	sub_groups[name] = []

	save_all()

	return True

def del_rss(name : str): # 只向用户通知
	global rss_tbl, sub_users, sub_groups

	if not name in rss_tbl:
		return []
	
	del rss_tbl[name]
	bak = sub_users[name][:]

	del sub_users[name]
	del sub_groups[name]

	save_all()

	return bak


def add_user(user_id : int, name : str):
	global sub_users

	if user_id in sub_users[name]:
		return False
	
	sub_users[name].append(user_id)
	
	save_all()

	return True

def del_user(user_id : int, name : str):
	global sub_users

	if not user_id in sub_users[name]:
		return False
	
	sub_users[name].remove(user_id)

	save_all()

	return True

def add_group(group_id : int, name : str):
	global sub_groups

	if group_id in sub_groups[name]:
		return False
	
	sub_groups[name].append(group_id)

	save_all()

	return True

def del_group(group_id : int, name : str):
	global sub_groups

	if not group_id in sub_groups[name]:
		return False
	
	sub_groups[name].remove(group_id)

	save_all()

	return True


def check_author(author : str):
	return author in rss_tbl

def get_url(author : str):
	return rss_tbl[author]

def get_rss_tbl():
	return dict(rss_tbl)


def query_users(author : str):
	return sub_users[author]

def query_groups(author : str):
	return sub_groups[author]


def query_author_by_user(user_id : int, name : str):
	a = []

	for o in rss_tbl:
		if user_id in sub_users[o]:
			a.append(o)
	
	return a

def query_author_by_group(group_id : int, name : str):
	a = []

	for o in rss_tbl:
		if group_id in sub_groups[o]:
			a.append(o)
	
	return a