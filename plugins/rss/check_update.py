import time
import datetime

last_checked = datetime.datetime.now()

def hell_its_about_time():
	global last_checked

	last_checked = datetime.datetime.utcnow()
	# UTC 标准时间

def work_time(t : time.struct_time):
	return datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday,
		t.tm_hour, t.tm_min, t.tm_sec)

def is_new(t : datetime.datetime):
	# o = datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

	return t > last_checked