# -*- coding: utf-8 -*-

import cherrypy, json, os, os.path, re, sys
from copy import deepcopy

from genshi.template import Context, TemplateLoader
from genshi.core import Markup

class JSONPirateEncoder(json.JSONEncoder):
	def default(self, o):
		try:
			return o.to_dict()
		except AttributeError:
			pass
		return JSONEncoder.default(self, o)

js_encoder = JSONPirateEncoder()

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
		
	t = int(round(t))
	try:
		ts = [u'Noll', u'En', u'Två', u'Tre', u'Fyra', u'Fem', u'Sex', u'Sju', u'Åtta', u'Nio', u'Tio', u'Elva', u'Tolv'][t]
	except IndexError:
		ts = str(t)
	
	if t>1:
		return  "%s %s " % (ts, pluralis)
	else:
		return "%s %s " % (ts, singularis)

def service_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return js_encoder.encode(value)

class GenshiHandler():
	def __init__(self, template, next_handler, type):
		self.template = template
		self.next_handler = next_handler
		self.type = type
	
	def __call__(self):
		context = Context(url=cherrypy.url)
		context.push(self.next_handler())
		stream = self.template.generate(context)
		cherrypy.response.headers['Content-Type'] = { 'xhtml': 'text/html', 'xml': 'application/xml' }[self.type]
		return stream.render(self.type)


class GenshiLoader():
	def __init__(self):
		self.loader = None
	
	def __call__(self, filename, dir, auto_reload = False, type = 'xhtml', sitemap_prio = '-1'):
		if self.loader == None:
			self.loader = TemplateLoader(dir, auto_reload=auto_reload)
		template = self.loader.load(filename)
		cherrypy.request.handler = GenshiHandler(template, cherrypy.request.handler, type)

genshi_template = GenshiLoader()
cherrypy.tools.genshi_template = cherrypy.Tool('before_handler', genshi_template)


sitemap = {}
def add_to_sitemap(priority = '0'):
	def decorator(func):
		sitemap['.'.join(func.__name__.replace('index', '/').rsplit('_', 1))] = priority
		return func
	return decorator

class Api():
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
	@add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='api/manual.html')
	def manual_html(self):
		return {}
	
	@cherrypy.expose
	@cherrypy.tools.json_out(handler = service_handler)
	def get_streams_js(self, url, rnd = None):
		return pirateplay.get_streams(url)

	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/get_streams.xml', type='xml')
	def get_streams_xml(self, url, rnd = None):
		return {'streams': [s.to_dict() for s in pirateplay.get_streams(url)]}
	
	#@cherrypy.expose(alias = 'generate_application.xml')
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/get_streams_old.xml', type='xml')
	def get_streams_old_xml(self, url, librtmp = '0', output_file = '-', parent_function = ''):
		streams = pirateplay.get_streams(url)
		
		if streams[0].url.startswith('rtmp') and librtmp == '0':
			return { 'streams': [{'url': pirateplay.rtmpdump_cmd(s.url, output_file), 'meta': s.metadict()} for s in streams] }
		elif '.m3u8' in streams[0].url or 'manifest.f4m' in streams[0].url:
			return { 'streams': [{ 'meta': { 'quality': u'Inkompatibel ström. Testa appen på Pirateplay.se.' }, 'url': 'http://localhost/' }] }
		else:
			return { 'streams': [s.to_dict() for s in streams] }
	
	@cherrypy.expose
	@cherrypy.tools.json_out(handler = service_handler)
	def services_js(self, titles = None, rnd = ''):
		s = self._filter_services(titles)
		return [self._convert_service_re(z) for z in s]

	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/services.xml', type='xml')
	def services_xml(self, titles = None, rnd = ''):
		return {'services': [self._convert_service_re(s).to_dict()
							for s in self._filter_services(titles)]}

class Root():
	def __init__(self):
		self.sitemap = {}
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='sitemap.xml', type='xml')
	def sitemap_xml(self):
		return { 'sites': sitemap }
	
	@cherrypy.expose
	def sitemap_html(self):
		return '<br />'.join(['<a href="%s">%s</a>' % ((i,)*2)
							for i in sitemap])
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='index.html')
	@add_to_sitemap('1.0')
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
	
	@cherrypy.expose
	@add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='app.html')
	def app_html(self):
		return  {}
	
	
	@cherrypy.expose
	@add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='library.html')
	def library_html(self):
		return {}
	
	@cherrypy.expose
	@add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='qna.html')
	def qna_html(self):
		qna_txt = open('data/qna.txt', 'r')
		qna = dict([pair.split('<!-- inner_delim -->') for pair in qna_txt.read().decode('utf-8').split('<!-- delim -->')])
		qna = dict([(Markup(q.strip()), Markup(a.strip())) for q, a in qna.items()])
		
		return {'qna': qna}
	
	@cherrypy.expose
	@add_to_sitemap('0.8')
	@cherrypy.tools.genshi_template(filename='player.html')
	def player_html(self):
		return dict(services = sorted([s.to_dict() for s in pirateplay.services if s.title != ''], key=lambda s: s['title']))
	
	@cherrypy.tools.genshi_template(filename='notfound.html')
	def default(self, *args, **kwargs):
		cherrypy.response.status = 404
		return {}
	
	api = Api()
	generate_application_xml = api.get_streams_old_xml


def get_streams_old_xml(url):
	return url

def _config(base_dir, port = 80):
	from string import maketrans
	
	return { 'global': {
			'server.environment': 'production',
			'server.socket_host': '0.0.0.0',
			'request.show_tracebacks': False,
			'server.socket_port': port,
			'tools.genshi_template.dir': os.path.join(base_dir, 'templates'),
			'tools.genshi_template.auto_reload': False },
		'/': {
			#'request.dispatch': cherrypy.dispatch.Dispatcher(translate=maketrans(';', '_')),
			'tools.encode.on': True,
			'tools.encode.encoding': 'utf-8'},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.root': base_dir,
			'tools.staticdir.dir': 'static' },
		'/playbrowser': {
			'tools.staticdir.on': True,
			'tools.staticdir.root': base_dir,
			'tools.staticdir.dir': 'static/playbrowser' },
		'/googleda06c6c176f69c2f.html': {
			'tools.staticfile.on': True,
			'tools.staticfile.filename': os.path.join(base_dir, 'googleda06c6c176f69c2f.html') } }

def application(environ, start_response):
	base_dir = environ.get('pirateplay_base_dir', '')
	port = int(environ.get('pirateplay_port', '80'))
	os.chdir(base_dir)
	
	if not base_dir in sys.path:
		sys.path.insert(0, base_dir)
	global pirateplay
	import lib.pirateplay as pirateplay
	
	config = _config(base_dir, port)
	
	cherrypy.tree.mount(Root(), config = config, script_name = environ.get('pirateplay_script_name', ''))
	cherrypy.config.update(config)
	return cherrypy.tree(environ, start_response)

if __name__ == "__main__":
	import lib.pirateplay as pirateplay
	
	base_dir = os.getcwd()
	
	config = _config(base_dir, 8081)
	config['global']['request.show_tracebacks'] = True
	config['global']['tools.genshi_template.auto_reload'] = True
	cherrypy.config.update(config)
	
	cherrypy.quickstart(Root(), config = config, script_name='')