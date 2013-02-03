from lib.pirateplay.rerequest2 import TemplateRequest
from common import redirect_handler

services = [{ 'title': 'DR-TV', 'url': 'http://dr.dk/tv',
				'items': [TemplateRequest( re = r'(?P<req_url>(http://)?(www\.)?dr\.dk/(TV/se/.+))' ),
						TemplateRequest(
							re = r'videoData:\s+{.+?resource:\s+"(?P<req_url>[^"]+)"',
							handlerchain = redirect_handler()),
						TemplateRequest( re = r'Location: (?P<req_url>.*?)\n' ),
						TemplateRequest(
							re = r'"uri":"(?P<rtmp_base>rtmpe?:\\/\\/vod\.dr\.dk\\/cms\\/)(?P<rtmp_path>[^"]+).*?"bitrateKbps":(?P<bitrate>\d+)',
							encode_vars = lambda v: { 'final_url': ('%(rtmp_base)s playpath=%(rtmp_path)s swfVfy=1 swfUrl=http://www.dr.dk/assets/swf/program-player.swf' % v).replace('\\', ''),
														'quality': '%(bitrate)s kbps' % v,
														'suffix-hint': 'flv' })] }]