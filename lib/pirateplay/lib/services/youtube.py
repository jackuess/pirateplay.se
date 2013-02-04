from ..rerequest import TemplateRequest
import subprocess

def youtube_dl(c):
	try:
		return subprocess.check_output(['youtube-dl', '-g', '--all-formats', '--get-format', c])
	except subprocess.CalledProcessError:
		return ''

services = [{ 'title': 'Youtube', 'url': 'http://youtube.com/', 'feed_url': 'http://gdata.youtube.com/feeds/base/videos?alt=rss',
			'items': [TemplateRequest(
						re = r'(http://)?(www\.)?youtube\.com/(?P<url>.+)' ),
					TemplateRequest(
						re = r'(?P<final_url>.+?)\n\d+ - (?P<quality>\d+x\d+)\n',
						decode_content = youtube_dl,
						 )] }]#encode_vars = lambda v: { } )] }]