from ..rerequest import TemplateRequest

video_re = r'playerWidth:\s(?P<width>\d+).*?playerHeight:\s(?P<height>\d+).*?videoUrl:\s"%s'

rtmp = { 'title': 'Aftonbladet-TV', 'url': 'http://aftonbladet.se/', 'feed_url': 'http://www.aftonbladet.se/webbtv/rss.xml',
		'items': [TemplateRequest(
					re = r'^(http://)?(www\.)?aftonbladet\.se/(?P<req_url>.+)',
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
						
tv_aftonbladet_se = { 'items': [TemplateRequest(
								re = r'^(?P<req_url>(http://)(www\.)?tv.aftonbladet.se/.+)' ),
							TemplateRequest(
								re = r'data-aptomaId="(?P<data_id>[^"]+)"',
								encode_vars = lambda v: { 'req_url': 'https://aftonbladet-play.drlib.aptoma.no/video/%(data_id)s.json' % v } ),
							TemplateRequest(
								re = r'"videoId":"(?P<video_id>[^"]+)"',
								encode_vars = lambda v: { 'req_url': 'http://aftonbladet-play.videodata.drvideo.aptoma.no/actions/video/?id=%(video_id)s' % v } ),
							TemplateRequest(
								re = r'"bitrate":(?P<quality>\d+).*?"paths":\[{"address":"(?P<base>[^"]+)".*?"path":"(?P<path>[^"]+)".*?"filename":"(?P<filename>[^"]+)"',
								encode_vars = lambda v: { 'final_url': 'http://%s/%s/%s'  % (v['base'], v['path'].replace('\\', ''), v['filename']),
														'quality': '%(quality)s kbps' % v,
														'suffix-hint': 'mp4' } )] }

services = [rtmp, http, tv_aftonbladet_se]