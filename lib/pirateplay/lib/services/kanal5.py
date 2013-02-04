from ..rerequest import TemplateRequest

get_video = 'http://www.kanal5play.se/api/getVideo?format=%(format)s&videoId=%(id)s'

def kilo_bitrate(v):
	return str(int(v['bitrate']) / 1000)

default = { 'title': 'Kanal5-play', 'url': 'http://kanal5play.se/', 'feed_url': 'http://www.kanal5play.se/rss?type=PROGRAM',
			'startvars': { 'format': 'FLASH', 'suffix-hint': 'flv' },
			'items': [TemplateRequest(
						re = r'^(http://)?(www\.)?kanal5play\.se/.*video/(?P<id>\d+)',
						encode_vars = lambda v: { 'req_url': get_video % v } ),
					TemplateRequest(
						re = r'"bitrate":(?P<bitrate>\d+).*?"source":"(?P<path>[^"]+)"(?=.*?"streamBaseUrl":"(?P<base>[^"]+)")',
						encode_vars = lambda v: { 'final_url': '%(base)s playpath=%(path)s swfVfy=1 swfUrl=http://www.kanal5play.se/flash/StandardPlayer.swf' % v,
												'subtitles': 'http://www.kanal5play.se/api/subtitles/%(id)s' % v,
												'quality': '%s kbps' % kilo_bitrate(v) } )] }

hls_force = { 'startvars': { 'format': 'IPHONE', 'suffix-hint': 'mp4' },
			'items': [TemplateRequest(
						re = r'^hls\+?(http://)?(www\.)?kanal5play\.se/.*video/(?P<id>\d+)',
						encode_vars = lambda v: { 'req_url': get_video % v } ),
					TemplateRequest(
						re = r'"source":"(?P<req_url>[^"]+)"' ),
					TemplateRequest(
						re = r'RESOLUTION=(?P<quality>\d+x\d+).*?(?P<final_url>http://[^\n]+)',
						encode_vars = lambda v: { 'quality': 'dynamisk',
												'subtitles': 'http://www.kanal5play.se/api/subtitles/%(id)s' % v } )] }
rtsp_force = { 'startvars': { 'format': 'ANDROID' },
				'items': [TemplateRequest(
							re = r'^rtsp\+?(http://)?(www\.)?kanal5play\.se/.*video/(?P<id>\d+)',
							encode_vars = lambda v: { 'req_url': get_video % v } ),
						TemplateRequest(
							re = r'"bitrate":(?P<bitrate>\d+).*?"source":"(?P<final_url>[^"]+)"',
							encode_vars = lambda v: { 'subtitles': 'http://www.kanal5play.se/api/subtitles/%(id)s' % v,
													'quality': '%s kbps' % kilo_bitrate(v) } )] }

services = [default, hls_force, rtsp_force]