from ..rerequest import TemplateRequest

def init_req(domain = 'tv4play', protocol = 'http://', query = ''):
	return TemplateRequest(
				re = r'^(%s)?(www\.)?%s\.se/.*(videoid|video_id|vid)=(?P<id>\d+).*' % (protocol, domain),
				encode_vars = lambda v: { 'req_url': ('http://premium.tv4play.se/api/web/asset/%(id)s/play' + query)  % v } )

rtmp = { 'title': 'TV4-play', 'url': 'http://tv4play.se/', 'feed_url': 'http://www.tv4play.se/rss/sport/ekwall_vs_lundh',
		'items': [init_req(),
				TemplateRequest(
					re = r'(<playbackStatus>(?P<status>\w+).*?)?<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?(?P<base>rtmpe?://[^<]+).*?(?P<url>mp4:/[^<]+)(?=.*?(?P<subtitles>http://((anytime)|(prima))\.tv4(play)?\.se/multimedia/vman/smiroot/[^<]+))?',
					encode_vars = lambda v: { 'final_url': '%(base)s playpath=%(url)s swfVfy=1 swfUrl=http://www.tv4play.se/flash/tv4playflashlets.swf' % v,
											'quality': '%(bitrate)s kbps' % v,
											'suffix-hint': 'flv' } )] }

hls = { 'items': [init_req(query='?protocol=hls'),
						TemplateRequest(
							re = r'<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?<url>(?P<final_url>http://[^<]+\.m3u8)(?=.*?(?P<subtitles>http://((anytime)|(prima))\.tv4(play)?\.se/multimedia/vman/smiroot/[^<]+))?',
							encode_vars = lambda v: { 'quality': '%(bitrate)s kbps' % v,
													'suffix-hint': 'mp4' } )] }

hds = { 'items': [init_req(),
				TemplateRequest(
					re = r'<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?<url>(?P<final_url>http://.*?\.mp4\.csmil/manifest\.f4m)</url>(?=.*?(?P<subtitles>http://((anytime)|(prima))\.tv4(play)?\.se/multimedia/vman/smiroot/[^<]+))?',
					encode_vars = lambda v: { 'final_url': '%(final_url)s?hdcore=2.7.6' % v,
											'quality': '%(bitrate)s kbps' % v,
											'required-player-version': '1' } )] }

http = { 'items': [init_req(),
				TemplateRequest(
					re = r'<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?<url>(?P<final_url>http://[^<]+).*?(?=.*?(?P<subtiltes>http://((anytime)|(prima))\.tv4(play)?\.se/multimedia/vman/smiroot/[^<]+))?',
					encode_vars = lambda v: { 'quality': '%(bitrate)s kbps' % v } )] }

#hls_force = { 'items': [init_req('tv4play', 'hls\+?http://', '?protocol=hls'),
						#http['items'][1]] }

fotbollskanalen = { 'title': 'Fotbollskanalen', 'url': 'http://fotbollskanalen.se/', 'sample_url': 'http://www.fotbollskanalen.se/video/?videoid=2194841',
				'items': [init_req('fotbollskanalen'),
						rtmp['items'][1]] }

services = [rtmp,
			hls,
			hds,
			http,
			#hls_force,
			fotbollskanalen]