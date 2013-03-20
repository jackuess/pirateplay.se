import cherrypy

class GenshiHandler():
	def __init__(self, template, next_handler, type):
		self.template = template
		self.next_handler = next_handler
		self.type = type
		
	def __call__(self):
		def replace_at(s):
			import sys
			from genshi.core import Markup
			for kind, data, pos in s:
				if kind == "TEXT" and not isinstance(data, Markup):
					yield kind, data.replace('@', '[snabel-a]'), pos
				else:
					yield kind, data, pos
		
		from urllib import quote
		from genshi.template import Context
		context = Context(url=cherrypy.url, quote=quote)
		context.push(self.next_handler())
		stream = self.template.generate(context)
		if self.type == 'xhtml':
			stream = stream | replace_at
		cherrypy.response.headers['Content-Type'] = { 'xhtml': 'text/html', 'xml': 'application/xml' }[self.type]
		return stream.render(self.type)

class GenshiLoader():
	def __init__(self):
		self.loader = None
	
	def __call__(self, filename, dir, auto_reload = False, type = 'xhtml', sitemap_prio = '-1'):
		from genshi.template import TemplateLoader
		if self.loader == None:
			self.loader = TemplateLoader(dir, auto_reload=auto_reload)
		template = self.loader.load(filename)
		cherrypy.request.handler = GenshiHandler(template, cherrypy.request.handler, type)