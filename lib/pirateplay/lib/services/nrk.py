from ..rerequest import TemplateRequest

services = [{ 'title': 'NRK-TV', 'url': 'http://tv.nrk.no/',
				'items': [ TemplateRequest(
								re = r'(?P<req_url>(http://)?tv.nrk.no/.+)',
								encode_vars = lambda v: { 'req_headers': { 'User-agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7' } } ),
						TemplateRequest(
							re = r'data-media="(?P<req_url>[^"]+)"(.*?data-subtitlesurl\s?=\s?"(?P<subtitles>[^"]+))?',
							encode_vars = lambda v: { 'subtitles': ('http://tv.nrk.no%(subtitles)s' % v if v['subtitles'] != None else None) } ),
						TemplateRequest(
							re = r'RESOLUTION=(?P<quality>\d+x\d+).*?(?P<url>http://[^\n]+)',
							encode_vars = lambda v: { 'final_url': '%(url)s' % v,
												'suffix-hint': 'mp4' })] }]