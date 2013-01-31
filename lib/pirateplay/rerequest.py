import re
import urllib2

DEBUG = False

def set_debug(debug):
	global DEBUG
	DEBUG = debug

def debug_print(s):
	if DEBUG:
		print ' DEBUG ' + s

class RequestChain:
	def __init__(self, title = '', url = '', feed_url = '', sample_url = '', items = []):
		self.title = title
		self.url = url
		self.feed_url = feed_url
		self.sample_url = sample_url
		self.items = items
	
	def get_streams(self, url):
		debug_print('Testing with service = ' + self.title)
		cumulated_vars = { 'sub': '' }
		content = url
		for item in self.items:
			new_vars = item.create_vars(content)
			
			if len(new_vars) < 1:
				break
			
			if item.is_last:
				return item.create_streams(new_vars, cumulated_vars)
			
			for v in new_vars:
				cumulated_vars.update(v)
			content = item.create_content(cumulated_vars)
		
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

	def del_nones(self, dict):
		for item in dict.items():
			if item[1] == None:
				del dict[item[0]]
		return dict
	
	def create_vars(self, content):
		content = self.decode_content(content)
		return [dict(match.groupdict(), **self.encode_vars(self.del_nones(match.groupdict())))
			for match in re.finditer(self.re, content, re.DOTALL)]
		
	def create_content(self, cumulated_vars):
		url = self.url_template % cumulated_vars
		url = self.decode_url(url)
		
		data = self.data_template % cumulated_vars
			
		req = urllib2.Request(url)

		if data != '':
			debug_print('Adding post data to request: ' + data)
			req.add_data(data)
				
		for header, value in self.headers.items():
			debug_print('Adding header to request: %s = %s' % (header, value))
			req.add_header(header, value)
			
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
	
	def remove_duplicates(self, streams):
		return dict([(s.url + s.meta, s) for s in streams]).values()
	
	def create_streams(self, new_vars, cumulated_vars):
		return self.remove_duplicates([Stream( url = self.decode_url( self.url_template % dict(cumulated_vars, **v) ),
												meta = self.decode_meta( self.meta_template % dict(cumulated_vars, **v) ) )
										for v in new_vars])

class Stream:
	def __init__(self, url, meta):
		self.url = url
		self.meta = meta
	
	def delete_empty_values(self, d):
		for key in d.keys():
			if d[key] == '':
				del d[key]
		return d
	
	def metadict(self):
		try:
			return self.delete_empty_values(dict([(x[0].strip(), x[1].strip()) for x in [i.strip().split('=') for i in self.meta.split(';')]]))
		except IndexError:
			return {}
	
	def to_dict(self):
		return { 'meta': self.metadict(), 'url': self.url }