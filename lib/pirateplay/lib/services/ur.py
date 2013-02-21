from ..rerequest import TemplateRequest

init_req = TemplateRequest(
					re = r'(http://)?(www\.)?(?P<domain>ur(play)?)\.se/(?P<req_url>.+)',
					encode_vars = lambda v: { 'req_url': 'http://%(domain)s.se/%(req_url)s' % v } )

hls = { 'title': 'UR-play', 'url': 'http://urplay.se/', 'feed_url': 'http://urplay.se/rss',
		'items': [init_req,
				TemplateRequest(
					re = r'file_html5":\s?"(?P<final_url>[^"]+)".*?"subtitles":\s?"(?P<subtitles>[^",]*)',
					encode_vars = lambda v: { 'final_url': ('http://130.242.59.75/%(final_url)s/playlist.m3u8' % v).replace('\\', ''),
											'suffix-hint': 'mp4',
											'subtitles': v.get('subtitles', '').replace('\\', '') % v } )] }

rtmp = { 'items': [init_req,
				TemplateRequest(
					re = r'file_flash":\s?"(?P<final_url>[^"]+\.(?P<ext>mp[34]))".*?"subtitles":\s?"(?P<subtitles>[^",]*)',
					encode_vars = lambda v: { 'final_url': ('rtmp://130.242.59.75/ondemand playpath=%(ext)s:/%(final_url)s app=ondemand' % v).replace('\\', ''),
											'suffix-hint': 'flv',
											'rtmpdump-realtime': True,
											'subtitles': v.get('subtitles', '').replace('\\', '') % v } )] }

services = [hls, rtmp]