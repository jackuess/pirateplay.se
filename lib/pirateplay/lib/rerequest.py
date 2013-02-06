import itertools, re, urllib2

DEBUG = False

def set_debug(debug):
	global DEBUG
	DEBUG = debug

def debug_print(s):
	if DEBUG:
		print(' DEBUG ' + s)

def del_empty_values(d):
	for key in d.keys():
		if d[key] == '' or d[key] == None:
			del d[key]
	return d

def req_key(req):
	key = req.get_full_url()
	key += str(req.header_items())
	if req.has_data():
		key += req.get_data()
	return key
	
def get_vars(requestchain, content, cache = {}):
	debug_print('Testing with service = %s' % requestchain.get('title', 'untitled'))
	cumulated_vars = requestchain.get('startvars', {})
	
	for item in requestchain.get('items', []):
		new_vars = item.create_vars(content, cumulated_vars)
		
		try:
			first = new_vars.next()
		except StopIteration:
			break
		
		new_vars = itertools.chain([first], new_vars)
		
		if 'final_url' in first:
			return [del_empty_values(dict(cumulated_vars, **v)) for v in new_vars]
		
		for v in new_vars:
			cumulated_vars.update(v)
		
		if 'req_url' in cumulated_vars:
			req = item.create_req(cumulated_vars)
			
			rk = req_key(req)
			if rk in cache:
				content = cache[rk]
			else:
				content = item.create_content(req)
				cache[rk] = content
		
	return []

class TemplateRequest:
	def __init__(self, re,
				encode_vars = lambda x: x, decode_content = lambda c, v: c,
				handlerchain = None):
		self.re = re
		self.encode_vars = encode_vars
		self.decode_content = decode_content
		self.handlerchain = handlerchain
	
	def create_vars(self, content, cumulated_vars):
		content = self.decode_content(content, cumulated_vars)
		
		#Make sure req_data and req_headers are empty
		if 'req_data' in cumulated_vars:
			del cumulated_vars['req_data']
		if 'req_headers' in cumulated_vars:
			del cumulated_vars['req_headers']
		
		for match in re.finditer(self.re, content, re.DOTALL):
			d = dict(cumulated_vars, **match.groupdict())
			d.update(self.encode_vars(d))
			yield d
	
	def create_req(self, cumulated_vars):
		req = urllib2.Request(cumulated_vars['req_url'])
		
		if 'req_data' in cumulated_vars:
			debug_print('Adding post data to request: ' + cumulated_vars['req_data'])
			req.add_data(cumulated_vars['req_data'])
		
		for header, value in cumulated_vars.get('req_headers', {}).items():
			debug_print('Adding header to request: %s = %s' % (header, value))
			req.add_header(header, value)
		return req
	
	def create_content(self, req):
		debug_print('Opening URL: ' + req.get_full_url())
		try:
			try:
				f = urllib2.build_opener(self.handlerchain).open(req)
			except TypeError:
				f = urllib2.urlopen(req)
			
			content = f.read()
			f.close()
		except (urllib2.HTTPError, urllib2.URLError):
			content = ''
		
		return content
	
	def to_dict(self):
		return { 'test': self.re }