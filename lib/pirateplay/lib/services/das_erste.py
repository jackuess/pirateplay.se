from ..rerequest import TemplateRequest

services = [{ 'title': 'Das Erste Mediathek', 'url': 'http://mediathek.daserste.de/',
				'items': [TemplateRequest( re = r'(?P<req_url>(http://)?mediathek\.daserste\.de/.*)' ),
						TemplateRequest(
							re = r'mediaCollection\.addMediaStream\(\d,\s(?P<quality>\d),\s"(?P<base>[^"]+)",\s"(?P<path>[^"]+)"',
							encode_vars = lambda v: { 'final_url': '%(base)s playpath=%(path)s' % v,
													'suffix-hint': 'flv' } )] }]