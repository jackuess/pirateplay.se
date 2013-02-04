from ..rerequest import TemplateRequest

services = [{ 'title': 'Filmarkivet', 'url': 'http://filmarkivet.se/', 'sample_url': 'http://filmarkivet.se/sv/Film/?movieid=220',
			'items': [TemplateRequest(
						re = r'(http://)?(www\.)?filmarkivet\.se/(?P<path>.*)',
						encode_vars = lambda v: { 'req_url': 'http://filmarkivet.se/%(path)s' % v } ),
					TemplateRequest(
						re = r"movieName\s=\s'(?P<movie_name>[^']+)'.*?streamer:\s'(?P<base>[^']+)'",
						encode_vars = lambda v: { 'final_url': '%(base)s%(movie_name)s' % v,
												'suffix-hint': 'flv' } )] }]