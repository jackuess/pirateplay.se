from ..rerequest import TemplateRequest

services = [{ 'title': 'Expressen-TV', 'url': 'http://expressen.se/tv/',
				'items': [TemplateRequest( re = r'(?P<req_url>(http://)?(www\.)?expressen\.se/(.+))' ),
						TemplateRequest( re = r'swfFileUrl:\s\'?(?P<swf_path>[^\']+)\'.*?xmlUrl:\s\'(?P<req_url>[^\']+)' ),
						TemplateRequest(
							re = r'<vurl bitrate="(?P<quality>\d+)"><!\[CDATA\[(?P<base>rtmpe?://[^/]+/[^/]+)/(?P<play_path>[^\]]+)(\.flv)?',
							encode_vars = lambda v: { 'final_url': '%(base)s playpath=%(play_path)s swfVfy=1 swfUrl=%(swf_path)s' % v,
													'suffix-hint': 'flv' } )] }]