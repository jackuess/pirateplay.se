from ..rerequest import TemplateRequest
from random import randint
from re import search
from urllib2 import HTTPError, urlopen

def fix_url(v):
	if v['domain'] == 'svt.se':
		try:
			f = urlopen('http://www.%(domain)s/%(path)s' % v)
			match = search(r'articleId=(\d+)', f.read())
			f.close()
			return { 'req_url': 'http://svtplay.se/video/%s?output=json' % match.group(1) }
		except (HTTPError, AttributeError):
			pass
	
	return { 'req_url': 'http://www.%(domain)s/%(path)s?output=json' % v }

init_req = TemplateRequest(
				re = r'^(http://)?(www\.)?(?P<domain>svt(play)?\.se)/(?P<path>[^?]+)',
				encode_vars = fix_url)

stream_re = r'"url":"(?P<url>%s[^"]+\.%s[^"]*)".*?(?=.*?"subtitleReferences":\[{"url":"(?P<subtitles>[^"]*))'
stream_re2 = r'"url":"(?P<url>%s[^"]+)".*?"bitrate":(?P<bitrate>\d+)(?=.*?"subtitleReferences":\[{"url":"(?P<subtitles>[^"]*))'


#Request chains

rtmp = { 'title': 'SVT-play', 'url': 'http://svtplay.se/',
		'items': [init_req,
				TemplateRequest(
					re = stream_re2 % 'rtmp',
					encode_vars = lambda v: { 'final_url': '%(url)s swfVfy=1 swfUrl=http://www.svtplay.se/public/swf/video/svtplayer-2012.15.swf' % v,
											'quality': 'quality=%(bitrate)s kbps' % v,
											'suffix-hint': 'flv' })] }

hls = { 'items': [init_req,
				TemplateRequest(
					re = stream_re % ('http://', 'm3u8'),
					encode_vars = lambda v: { 'req_url': '%(url)s' % v }),
				TemplateRequest(
					re = r'RESOLUTION=(?P<quality>\d+x\d+).*?(?P<url>http://[^\n]+)',
					encode_vars = lambda v: { 'final_url': '%(url)s' % v,
												'suffix-hint': 'mp4' })] }

hds_fake = { 'items': [init_req,
					TemplateRequest(
						re = stream_re % ('http://', 'f4m'),
						encode_vars = lambda v: { 'req_url': '%s' % v['url'].replace('manifest.f4m', 'master.m3u8').replace('akamaihd.net/z/', 'akamaihd.net/i/') }),
					hls['items'][2]] }

hds = { 'startvars': { 'guid': ''.join(chr(65 + randint(0, 25)) for i in range(12)) }, 
		'items': [init_req,
				TemplateRequest(
					re = stream_re % ('http://', 'f4m'),
					encode_vars = lambda v: { 'final_url': '%(url)s?hdcore=2.8.0&g=%(guid)s' % v,
											'quality': 'dynamisk',
											'suffix-hint': 'flv',
											'required-player-version': '1' })] }

http = { 'items': [init_req,
				TemplateRequest(
					re = stream_re2 % 'http://',
					encode_vars = lambda v: { 'final_url': '%(url)s' % v,
											'quality': '%(bitrate)s kbps' % v,
											'suffix-hint': 'flv' })] }

services = [rtmp,
			hls,
			hds_fake,
			hds,
			http]