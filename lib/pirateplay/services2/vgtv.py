from lib.pirateplay.rerequest2 import TemplateRequest

services = [{ 'title': 'VGTV', 'url': 'http://vgtv.no/',
			'items': [TemplateRequest(
						re = r'(http://)?(www\.)?vgtv\.no/.*/(?P<id>\d+)/',
						encode_vars = lambda v: { 'req_url': 'http://www.vgtv.no/data/actions/videostatus/?id=%(id)s' % v } ),
					TemplateRequest(
						re = r'{"width":(?P<width>\d+),"height":(?P<height>\d+),"bitrate":(?P<bitrate>\d+),"paths":\[{"address":"(?P<adress>[^"]+)","port":80,"application":"","path":"(?P<path>download\\/[^"]+)","filename":"(?P<filename>[^"]+)"',
						encode_vars = lambda v: { 'final_url': ('http://%(adress)s/%(path)s/%(filename)s' % v).replace('\\/', '/'),
												'quality': '%(width)sx%(height)s' % v } )] }]