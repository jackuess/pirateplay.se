import re
import urllib2

DEBUG = False

def set_debug(debug):
	global DEBUG
	DEBUG = debug

def debug_print(s):
	if DEBUG:
		print ' DEBUG ' + s

def del_nones(dict):
	for item in dict.items():
		if item[1] == None:
			del dict[item[0]]
	return dict

class RequestChain:
	def __init__(self, title = '', url = '', feed_url = '', sample_url = '', items = []):
		self.title = title
		self.url = url
		self.feed_url = feed_url
		self.sample_url = sample_url
		self.items = items
	
	def get_streams(self, url):
		debug_print('Testing with service = ' + self.title)
		vars = { 'sub': '' }
		content = url
		for item in self.items:
			item.set_content(content, vars)
			
			if item.is_last:
				streams = item.get_streams()
				item.release_content()
				return streams
			else:
				reqs = item.get_requests()
				if len(reqs) > 0:
					for req in reqs:
						debug_print('Opening URL: ' + req.get_full_url())
						try:
							if item.handlerchain != None:
								f = urllib2.build_opener(item.handlerchain).open(req)
							else:
								f = urllib2.urlopen(req)
							content = f.read()
							f.close()
						except urllib2.HTTPError:
							content = ''
						try:
							vars.update(item.get_vars())
						except TypeError:
							pass
				else:
					item.release_content()
					return []
			item.release_content()
		return []
	
	def to_dict(self):
		d = {}
		if self.title != '':
			d['title'] = self.title
		if self.url != '':
			d['url'] = self.url
		if self.feed_url != '':
			d['feed_url'] = self.feed_url
		if self.sample_url != '':
			d['sample_url'] = self.sample_url
		try:
			d['test'] = self.items[0].re
		except IndexError:
			pass
		
		return d


class TemplateRequest:
	def __init__(self, re,
				url_template = '', meta_template = '', data_template = '',
				encode_vars = lambda x: x, decode_url = lambda x: x, decode_meta = lambda x: x, decode_content = lambda x: x,
				headers = {}, handlerchain = None,
				is_last = False):
		self.re = re
		self.url_template = url_template
		self.meta_template = meta_template
		self.encode_vars = encode_vars
		self.decode_url = decode_url
		self.decode_meta = decode_meta
		self.decode_content = decode_content
		self.headers = headers
		self.handlerchain = handlerchain
		self.data_template = data_template
		self.is_last = is_last
		
		self.requests = []
		self.streams = []
	
	def set_content(self, content, old_vars):
		self.requests = []
		self.streams = []
		self.content = self.decode_content(content)
		self.curr_vars = old_vars
		
		for match in re.finditer(self.re, self.content, re.DOTALL):
			self.curr_vars.update(del_nones(match.groupdict()))
			self.add_request()
			
	def release_content(self):
		self.requests = None
		self.streams = None
		self.content = None
		self.curr_vars = None
					
	def get_vars(self):
		return self.curr_vars
	
	def process(self):
		self.curr_vars.update(self.encode_vars(self.curr_vars))
		
		self.url = self.url_template % self.curr_vars
		self.meta = self.meta_template % self.curr_vars
		self.data = self.data_template % self.curr_vars
		
		self.url = self.decode_url(self.url)
		self.meta = self.decode_meta(self.meta)
	
	def get_streams(self):
		#Remove duplicates in self.streams before returning
		return dict([(s.url + s.meta, s) for s in self.streams]).values()
	
	def get_requests(self):
		return self.requests
	
	def add_request(self):
		self.process()
		
		if self.is_last:
			self.streams.append(Stream(self.url, self.meta))
			return
		
		req = urllib2.Request(self.url)

		if self.data != '':
			debug_print('Adding post data to request: ' + self.data)
			req.add_data(self.data)
			
		for header, value in self.headers.items():
			debug_print('Adding header to request: %s = %s' % (header, value))
			req.add_header(header, value)
		
		self.requests.append(req)

def delete_empty_values(d):
	for key in d.keys():
		if d[key] == '':
			del d[key]
	return d

class Stream:
	def __init__(self, url, meta):
		self.url = url
		self.meta = meta
	
	def metadict(self):
		try:
			return delete_empty_values(dict([(x[0].strip(), x[1].strip()) for x in [i.strip().split('=') for i in self.meta.split(';')]]))
		except IndexError:
			return {}
	
	def to_dict(self):
		return { 'meta': self.metadict(), 'url': self.url }