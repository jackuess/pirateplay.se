# -*- coding: utf-8 -*-

import cherrypy, json, re, sys
from copy import deepcopy

from genshi.template import TemplateLoader
from genshi.core import Markup

class JSONPirateEncoder(json.JSONEncoder):
	def default(self, o):
		try:
			return o.to_dict()
		except AttributeError:
			pass
		return JSONEncoder.default(self, o)

def relative_time(s):
	if s>31536000:
		t = s/31536000
		singularis = pluralis = u"år"
	elif s>2592000:
		t = s/2592000;
		singularis, pluralis = (u"månad", u"månader")
	elif s>86400:
		t = s/86400;
		singularis, pluralis  = (u"dag", u"dagar")
	elif s>3600:
		t = s/3600;
		singularis, pluralis = (u"timme", u"timmar")
	elif s>60:
		t = s/60;
		singularis, pluralis = (u"minut", u"minuter")
	else:
		t = s;
		singularis, pluralis = (u"sekund", u"sekunder")
		
	t = round(t)
	if t>1:
		return  "%d %s " % (t, pluralis)
	else:
		return "%d %s " % (t, singularis)


class Root(object):
	def _add_to_site_map(func):
		func.add_to_site_map = True
		return func
	def __init__(self, template_dir):
		self._tmpl_loader = TemplateLoader(template_dir, auto_reload=True)
		self._jsencoder = JSONPirateEncoder()
		self._templates = {}

	def _render_template(self, template_name, args = {}, type = 'xhtml'):
		try:
			self._templates[template_name]
		except KeyError:
			self._templates[template_name] = self._tmpl_loader.load(template_name)
		return self._templates[template_name].generate(**args).render(type)

	@cherrypy.expose
	def get_streams_js(self, url, rnd = None):
		cherrypy.response.headers['Content-Type'] = 'application/json'
		return self._jsencoder.encode(pirateplay.get_streams(url))

	@cherrypy.expose
	def get_streams_xml(self, url, rnd = None):
		cherrypy.response.headers['Content-Type'] = 'application/xml'
		
		return self._render_template(template_name = 'get_streams.xml',
									args = dict(streams = [s.to_dict()
											for s in pirateplay.get_streams(url)]),
									type = 'xml')
	
	@cherrypy.expose
	def get_streams_old_xml(self, url, rnd = None):
		cherrypy.response.headers['Content-Type'] = 'application/xml'
		
		return self._render_template(template_name = 'get_streams_old.xml',
									args = dict(streams = [s.to_dict()
											for s in pirateplay.get_streams(url)]),
									type = 'xml')

	def _convert_service_re(self, service):
		s = deepcopy(service)
		try:
			s.items[0].re = re.sub(r'(\(\?P<\w+>)|(\(\?:)', '(', service.items[0].re)
		except IndexError:
			return service
		else:
			return s
		
	def _filter_services(self, titles):
		try:
			titles = [t.lower() for t in titles.split(',')]
		except AttributeError:
			return pirateplay.services
		else:
			return [s for s in pirateplay.services if s.title.lower() in titles]
	
	@cherrypy.expose
	def services_js(self, titles = None, rnd = ''):
		cherrypy.response.headers['Content-Type'] = 'application/json'
		
		s = self._filter_services(titles)
		s = [self._convert_service_re(z) for z in s]
		
		return self._jsencoder.encode(s)

	@cherrypy.expose
	def services_xml(self, titles = None, rnd = ''):
		cherrypy.response.headers['Content-Type'] = 'application/xml'
		
		return self._render_template(template_name = 'services.xml',
									args = dict(services = [self._convert_service_re(s).to_dict()
											for s in self._filter_services(titles)]),
									type = 'xml')
	
	@cherrypy.expose
	def sitemap_xml(self):
		cherrypy.response.headers['Content-Type'] = 'application/xml'
		sites = [i for i in dir(self) if getattr(getattr(self, i), 'add_to_site_map', False)]
		return '<sites><site>' + '</site><site>'.join(sites) + '</site></sites>'
		
	
	@cherrypy.expose
	@_add_to_site_map
	def index_html(self):
		from urllib2 import urlopen
		import datetime
		
		now = datetime.datetime.now()
		tweets = [{'text': Markup(re.sub(r'(https?://\S+)', '<a href="\\1">\\1</a>', tweet['text'], flags=re.IGNORECASE)),
				'time': unicode(relative_time((now - datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")).total_seconds()))}
				for tweet in json.load(urlopen('http://twitter.com/statuses/user_timeline.json?screen_name=pirateplay_se&count=10'))]
		
		services_se = sorted([s.to_dict() for s in pirateplay.services if len(s.items) > 0 and '\.se/' in s.items[0].re and s.title != ''], key=lambda s: s['title'])
		services_other = sorted([s.to_dict() for s in pirateplay.services if len(s.items) > 0 and not '\.se/' in s.items[0].re and s.title != ''], key=lambda s: s['title'])
		
		return self._render_template(template_name = 'index.html', args = dict(services_se = services_se, services_other = services_other, tweets = tweets))
	
	@cherrypy.expose
	@_add_to_site_map
	def app_html(self):
		return self._render_template(template_name = 'app.html')
	
	@cherrypy.expose
	def api_html(self):
		return self._render_template(template_name = 'api.html')
	
	@cherrypy.expose
	def library_html(self):
		return self._render_template(template_name = 'library.html')
	
	@cherrypy.expose
	def qna_html(self):
		qna_txt = open('data/qna.txt', 'r')
		qna = dict([pair.split('<!-- inner_delim -->') for pair in qna_txt.read().decode('utf-8').split('<!-- delim -->')])
		qna = dict([(Markup(q.strip()), Markup(a.strip())) for q, a in qna.items()])
		
		return self._render_template(template_name = 'qna.html', args = {'qna': qna})
	
	def _unfinished(func):
		@cherrypy.expose
		def unfinished(self):
			return self._render_template(template_name = 'unfinished.html')
		return unfinished
	
	@cherrypy.expose
	def player_html(self):
		return self._render_template(template_name = 'player.html',
									args = dict(services = sorted([s.to_dict() for s in pirateplay.services if s.title != ''], key=lambda s: s['title'])))

_config = { 'global': {
			'server.environment': 'production',
			'server.socket_host': '0.0.0.0',
			'server.socket_port': 8080 },
		'/': {
			'tools.encode.on': True,
			'tools.encode.encoding': 'utf8' },
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': 'static' } }

def application(environ, start_response):
	from os import chdir
	base_dir = environ.get('pirateplay_base_dir', '')
	chdir(base_dir)
	
	if not base_dir in sys.path:
		sys.path.append(base_dir)
	global pirateplay
	import lib.pirateplay as pirateplay
	
	_config['/']['tools.staticdir.root'] = base_dir
	cherrypy.tree.mount(Root(template_dir = base_dir + '/templates'), config = _config, script_name = environ.get('pirateplay_script_name', ''))
	return cherrypy.tree(environ, start_response)

if __name__ == "__main__":
	import lib.pirateplay as pirateplay
	
	from os import getcwd
	base_dir = getcwd()
	
	_config['global']['server.socket_port'] = 8081
	_config['/']['tools.staticdir.root'] = base_dir
	cherrypy.quickstart(Root(template_dir = base_dir + '/templates'), config = _config, script_name='/pirateplay2')