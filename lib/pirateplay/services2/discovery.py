from lib.pirateplay.rerequest2 import TemplateRequest

services = [{ 'title': 'Discovery', 'url': 'http://dsc.discovery.com/',
				'items': [TemplateRequest( re = r'(?P<req_url>(http://)?dsc\.discovery\.com/.+)' ),
						TemplateRequest(
							re = r'"clips":\s*\[\s*{\s*"clipRefId"\s*:\s*"(?P<id>[^"]+)"',
							encode_vars = lambda v: { 'req_url': 'http://static.discoverymedia.com/videos/components/dsc/%(id)s/smil-service.smil' % v } ),
						TemplateRequest( re = r'<meta\s+name="httpBase"\s+content="(?P<base>[^"]+)".*?' ),
						TemplateRequest(
							re = r'<video\s+src="(?P<path>[^"]+)"\s+system-bitrate="(?P<bitrate>\d+)"',
							encode_vars = lambda v: { 'final_url': '%(base)s/%(path)s' % v,
														'quality': '%s kbps' % str(int(v['bitrate'])/1000),
														'suffix-hint': 'flv' } )] }]