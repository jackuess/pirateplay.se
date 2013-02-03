from cStringIO import StringIO
from urllib2 import HTTPRedirectHandler

class redirect_handler(HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		return StringIO(str(headers))