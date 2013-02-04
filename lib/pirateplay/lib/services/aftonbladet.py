from ..rerequest import TemplateRequest

video_re = r'playerWidth:\s(?P<width>\d+).*?playerHeight:\s(?P<height>\d+).*?videoUrl:\s"%s'

rtmp = { 'title': 'Aftonbladet-TV', 'url': 'http://aftonbladet.se/', 'feed_url': 'http://www.aftonbladet.se/webbtv/rss.xml',
		'items': [TemplateRequest(
					re = r'(http://)?(www\.)?aftonbladet\.se/(?P<req_url>.+)',
					encode_vars = lambda v: { 'req_url': 'http://aftonbladet.se/%(req_url)s' % v } ),
				TemplateRequest(
					re = video_re % '(?P<base>rtmp://([^/]+)/[^/]+/)(?P<url>[^"]+)".*?videoIsLive:\s(?P<live>true|false)',
					encode_vars = lambda v: { 'final_url': ('%(base)s playpath=%(url)s live=%(live)s' % v).replace('live=true', 'live=1').replace(' live=false', ''),
												'quality': '%(width)sx%(height)s' % v,
												'suffix-hint': 'flv' } )] }

http = { 'items': [rtmp['items'][0],
					TemplateRequest(
						re = video_re % '(?P<final_url>[^"]+)"',
						encode_vars = lambda v: { 'quality': '%(width)sx%(height)s' % v,
													'suffix-hint': 'flv' } )] }

services = [rtmp, http]