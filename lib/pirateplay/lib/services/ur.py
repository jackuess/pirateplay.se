from ..rerequest import TemplateRequest

services = [{ 'title': 'UR-play', 'url': 'http://urplay.se/', 'feed_url': 'http://urplay.se/rss',
		'items': [TemplateRequest(
					re = r'(http://)?(www\.)?(?P<domain>ur(play)?)\.se/(?P<req_url>.+)',
					encode_vars = lambda v: { 'req_url': 'http://%(domain)s.se/%(req_url)s' % v } ),
				TemplateRequest(
					re = r'file_flash":\s?"(?P<final_url>[^"]+\.(?P<ext>mp[34]))".*?"subtitles":\s?"(?P<subtitles>[^",]+)',
					encode_vars = lambda v: { 'final_url': ('rtmp://130.242.59.75/ondemand playpath=%(ext)s:/%(final_url)s app=ondemand' % v).replace('\\', ''),
											'suffix-hint': 'flv',
											'rtmpdump-realtime': True,
											'subtitles': v.get('subtitles', '').replace('\\', '') % v } )] }]