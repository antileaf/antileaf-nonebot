import feedparser
import time, datetime

from .check_update import work_time

class Article:
	def __init__(self, author, title, summary, tags, link, published : datetime.datetime):
		self.author = author
		self.title = title
		self.summary = summary
		self.tags = tags
		self.link = link
		self.published = published


def parse(feed : feedparser.util.FeedParserDict) -> list:
	# entries = feed['entries']

	return [Article(o['author'], o['title'], o['summary'], [u['term'] for u in o['tags']], o['link'], work_time(o['published_parsed'])) for o in feed['entries']]

def get_feed(url : str) -> feedparser.util.FeedParserDict:
	return feedparser.parse(url)


def get_articles(url : str) -> list:
	return parse(get_feed(url))


def generate_notice(o : Article):
	return f'''\
标题：{o.title}
地址：{o.link}
发布时间：{str(o.published)}
摘要：{o.summary}
标签：{'，'.join(o.tags)}\
	'''