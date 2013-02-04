from ..rerequest import TemplateRequest
import subprocess

services = [{ 'title': 'Youtube', 'url': 'http://youtube.com/', 'feed_url': 'http://gdata.youtube.com/feeds/base/videos?alt=rss',
			'items': [TemplateRequest(
						re = r'(http://)?(www\.)?youtube\.com/(?P<url>.+)' ),
					TemplateRequest(
						re = r'(?P<final_url>.+?)\n\d+ - (?P<quality>\d+x\d+)\n',
						decode_content = lambda c: subprocess.check_output(['youtube-dl', '-g', '--all-formats', '--get-format', c]),
						encode_vars = lambda v: { } )] }]