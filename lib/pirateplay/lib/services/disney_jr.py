from ..rerequest import TemplateRequest

services = [{ 'title': 'Disney Junior', 'url': 'http://www.disney.se/disney-junior/innehall/video.jsp',
			'items': [TemplateRequest( re = r'(?P<req_url>(http://)?(www\.)?disney\.se/disney-junior/.+)' ),
					TemplateRequest(
						re = r"config\.firstVideoSource\s=\s'(?P<play_path>[^']+)'.*?config\.rtmpeServer\s=\s'(?P<base>[^']+)'",
						encode_vars = lambda v: { 'final_url': '%(base)s playpath=mp4:/%(play_path)s swfVfy=1 swfUrl=http://www.disney.se/cms_res/disney-junior/flash/video_hub_player/disney_player.swf' % v,
												'suffix-hint': 'flv' } )] }]