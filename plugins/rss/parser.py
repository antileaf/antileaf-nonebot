import feedparser
import time, datetime

from typing import *

from .check_update import work_time

class Blog: # feed 返回的信息没有 owner
	def __init__(self, link : str, title : str, subtitle : Optional[str]):
		self.link = link
		self.title = title
		self.subtitle = subtitle


class Article:
	def __init__(self, author, title, summary, tags, link, published : Optional[datetime.datetime]):
		self.author = author
		self.title = title
		self.summary = summary
		self.tags = tags
		self.link = link
		self.published = published


def parse_blog(feed : feedparser.util.FeedParserDict) -> Blog:
	info = feed['feed']

	link = info['link']
	title = info['title']
	subtitle = info['subtitle'] if 'subtitle' in info else ''

	return Blog(link, title, subtitle)


def handle_summary(summary : str):
	'''
	应对不同情况，规范 summary 格式
	'''

	if len(summary) > 300:
		return ''

	summary = summary.replace('&#160;', ' ')
	summary = summary.replace('&#8230;', '…')

	return summary


def parse_articles(feed : feedparser.util.FeedParserDict) -> List[Article]:
	'''
	把 xml 转换成 list[Article]
	'''

	entries = feed['entries']

	articles = []

	for o in entries:
		author = o['author'] if 'author' in o else ''

		title = o['title'] if 'title' in o else ''

		summary = o['summary'] if 'summary' in o else ''
		if 'feed' in feed and 'subtitle' in feed['feed'] and summary == feed['feed']['subtitle']:
			summary = ''

		tags = [u['term'] for u in o['tags']] if 'tags' in o else []

		link = o['link'] if 'link' in o else ''

		published = work_time(o['published_parsed']) if 'published_parsed' in o \
			else datetime.datetime(o['published']) if 'published' in o else None
		
		if summary:
			summary = handle_summary(summary)
		
		articles.append(Article(author, title, summary, tags, link, published))

	# print('successfully parsed!')

	return articles

	# return [Article(o['author'], o['title'], o['summary'], [u['term'] for u in o['tags']], o['link'], work_time(o['published_parsed'])) for o in feed['entries']]


def get_feed(feed_url : str) -> feedparser.util.FeedParserDict:
	res = feedparser.parse(feed_url)

	# print('fetched successfully!\n')

	return res


def get_blog(feed_url : str) -> Blog:
	'''
	封装后的方法，获取指定 feed url 的博客信息
	'''

	return parse_blog(get_feed(feed_url))


def generate_blog_info(o : Blog) -> str:
	'''
	对给定的博客生成博客信息
	'''
	v = []

	v.append(f'地址：{o.link}')
	v.append(f'标题：{o.title}')
	
	if o.subtitle:
		v.append(f'副标题：{o.subtitle}')
	
	return '\n'.join(v)


def get_articles(feed_url : str) -> List[Article]:
	'''
	封装后的方法，获取指定 feed url 的最新文章
	'''

	return parse_articles(get_feed(feed_url))


def generate_article_info(o : Article) -> str:
	'''
	对给定的文章生成摘要信息
	'''

	v = []

	if o.title:
		v.append(f'标题：{o.title}')
	if o.link:
		v.append(f'地址：{o.link}')
	if o.published:
		v.append(f'发布时间：{str(o.published)}')
	if o.summary:
		v.append(f'摘要：{o.summary}')
	if o.tags:
		v.append(f'标签：{"，".join(o.tags)}')

	return '\n'.join(v)