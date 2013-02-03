from lib.pirateplay.rerequest2 import TemplateRequest

services = [{ 'title': 'SR', 'url': 'http://sr.se/', 'feed_url': 'http://sverigesradio.se/api/rss/broadcast/516',
				'items': [ TemplateRequest(
							re = r'(http://)?(www\.)?sverigesradio\.se/(?P<req_url>.+)',
							encode_vars = lambda v: { 'req_url': 'http://sverigesradio.se/%(req_url)s' % v } ),
						TemplateRequest(
							re = r'<ref href="(?P<final_url>[^"]+)"')] }]