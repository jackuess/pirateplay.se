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
	def _template(template, type = 'xhtml', sitemap_prio = '0'):
		def decorator(func):
			@cherrypy.expose
			def wrapped(*args, **kwargs):
				cherrypy.response.headers['Content-Type'] = { 'xhtml': 'text/html', 'xml': 'application/xml' }[type]
				
				vars = func(*args, **kwargs)
				this = args[0] #Self
				
				return this._render_template(template, vars, type)
			
			wrapped.template = template
			wrapped.sitemap_prio = sitemap_prio
			return wrapped
		return decorator
	
	def _json(func):
		@cherrypy.expose
		def wrapped(*args, **kwargs):
			cherrypy.response.headers['Content-Type'] = 'application/json'
			js = func(*args, **kwargs)
			this = args[0]
			return this._jsencoder.encode(js)
		return wrapped
	
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

	@_json
	def get_streams_js(self, url, rnd = None):
		return pirateplay.get_streams(url)

	@_template('get_streams.xml', type='xml')
	def get_streams_xml(self, url, rnd = None):
		return {'streams': [s.to_dict() for s in pirateplay.get_streams(url)]}
	
	@_template('get_streams_old.xml', type='xml')
	def get_streams_old_xml(self, url, rnd = None):
		return { 'streams': [s.to_dict() for s in pirateplay.get_streams(url)] }
	
	@_json
	def services_js(self, titles = None, rnd = ''):
		s = self._filter_services(titles)
		return [self._convert_service_re(z) for z in s]

	@_template('services.xml', type='xml')
	def services_xml(self, titles = None, rnd = ''):
		return {'services': [self._convert_service_re(s).to_dict()
							for s in self._filter_services(titles)]}
	
	@_template('sitemap.xml', 'xml')
	def sitemap_xml(self):
		return { 'sites': [(getattr(getattr(self, i), 'template'), getattr(getattr(self, i), 'sitemap_prio')) for i in dir(self) if getattr(getattr(self, i), 'sitemap_prio', '0') != '0'] }
	
	@_template('index.html', sitemap_prio = '1.0')
	def index(self):
		from urllib2 import urlopen
		import datetime
		
		now = datetime.datetime.now()
		tweets = [{'text': Markup(re.sub(r'(https?://\S+)', '<a href="\\1">\\1</a>', tweet['text'], flags=re.IGNORECASE)),
				'time': unicode(relative_time((now - datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")).total_seconds()))}
				for tweet in json.load(urlopen('http://twitter.com/statuses/user_timeline.json?screen_name=pirateplay_se&count=10'))]
		
		services_se = sorted([s.to_dict() for s in pirateplay.services if len(s.items) > 0 and '\.se/' in s.items[0].re and s.title != ''], key=lambda s: s['title'])
		services_other = sorted([s.to_dict() for s in pirateplay.services if len(s.items) > 0 and not '\.se/' in s.items[0].re and s.title != ''], key=lambda s: s['title'])
		
		return dict(services_se = services_se, services_other = services_other, tweets = tweets)
	
	@_template('app.html', sitemap_prio = '0.5')
	def app_html(self):
		return  {}
	
	@_template('api.html', sitemap_prio = '0.5')
	def api_html(self):
		return {}
	
	@_template('library.html', sitemap_prio = '0.5')
	def library_html(self):
		return {}
	
	@_template('qna.html', sitemap_prio = '0.5')
	def qna_html(self):
		qna_txt = open('data/qna.txt', 'r')
		qna = dict([pair.split('<!-- inner_delim -->') for pair in qna_txt.read().decode('utf-8').split('<!-- delim -->')])
		qna = dict([(Markup(q.strip()), Markup(a.strip())) for q, a in qna.items()])
		
		return {'qna': qna}
	
	@_template('player.html', sitemap_prio = '0.5')
	def player_html(self):
		return dict(services = sorted([s.to_dict() for s in pirateplay.services if s.title != ''], key=lambda s: s['title']))


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