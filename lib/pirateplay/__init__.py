from get_stream import get_streams, rtmpdump_cmd#, services
from lib.services import services

from json import JSONEncoder
class JSONEncoder(JSONEncoder):
	def default(self, o):
		try:
			return o.to_dict()
		except AttributeError:
			pass
		return JSONEncoder.default(self, o)

js_encoder = JSONEncoder()