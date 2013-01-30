from lxml import etree
from os import system
from random import randint
from traceback import format_exc
from urllib2 import urlopen, HTTPError
from sys import argv

import services
from main import get_streams, rtmpdump_cmd
from rerequest import set_debug

def test_cmd(cmd):
	status = system(cmd) >> 8 #High byte is exit status (low byte is pid who killed)
	if status == 1:
		print ansi['red'] + 'Failed!' + ansi['reset']
	else:
		print ansi['green'] + 'Success!' + ansi['reset']

ansi = {'red': '\033[31m',
	'green': '\033[32m',
	'blue': '\033[36m',
	'reset': '\033[0m'}

cmd_template = { 'http': 'curl -r 0-102400 -o /dev/null "%s"',
				'rtmp': '%s' }

if len(argv) > 1:
	services.services = [service for service in services.services if service.title.lower() == argv[-1].lower()]

for service in services.services:
	try:
		f = urlopen(service.feed_url)
		tree = etree.parse(f)
		f.close()
		rnd = randint(1, int(tree.xpath('count(/rss/channel/item)')))
		url = tree.xpath('/rss/channel/item[%s]/link/text()' % rnd)[0]
		title = tree.xpath('/rss/channel/item[%s]/title/text()' % rnd)[0]
	except (ValueError, HTTPError):
		if service.sample_url == '':
			continue
		url = service.sample_url
		title = 'Unknown'

	print
	print ansi['blue'] + service.title + ansi['reset']
	print title + ' - ' + url
	streams = get_streams(url)
	if len(streams) > 0:
		stream_url = streams[0].url
		if stream_url.startswith('rtmp'):
			test_cmd(rtmpdump_cmd(stream_url + ' -q -B 20', '/dev/null'))
		elif stream_url.startswith('http'):
			test_cmd('curl -r 0-102400 -o /dev/null "%s"' % stream_url)
		else:
			print ansi['red'] + 'Unknown protocol of url: ' + stream_url
	else:
		print ansi['red'] + 'Nothing found!' + ansi['reset']