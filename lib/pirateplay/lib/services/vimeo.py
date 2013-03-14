from ..rerequest import TemplateRequest
from common import redirect_handler

headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0' }
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-us,en;q=0.5',
}

services = [{ 'title': 'Vimeo', 'url': 'http://vimeo.com/', 'feed_url': 'http://vimeo.com/channels/staffpicks/videos/rss',
			'items': [TemplateRequest(
						re = r'(http://)?(www\.)?vimeo\.com/.*?(?P<id>\d+)$',
						encode_vars = lambda v: { 'req_url': 'http://vimeo.com/%(id)s' % v}),#,
												#'req_headers': headers } ),
					TemplateRequest(
						re = r'"timestamp":(?P<time>\d+).*?"signature":"(?P<sig>[^"]+)".*?((h264)|(vp6)|(vp8))":\["(?P<quality>[^"]+)',
						encode_vars = lambda v: { 'req_url': 'http://player.vimeo.com/play_redirect?clip_id=%(id)s&sig=%(sig)s&time=%(time)s&quality=%(quality)s&codecs=VP6,VP8,H264&type=moogaloop_local&embed_location=' % v},#,
												#'req_headers': headers },
						handlerchain = redirect_handler()),
					TemplateRequest( re = r'Location: (?P<final_url>.*?)\s' )] }]
