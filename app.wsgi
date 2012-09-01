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

class Root(object):
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
	def get_streams_js(self, url = 'http://www.tv4play.se/sport/ekwall_vs_lundh?title=ekwall_vs_lundh_med_may_mahlangu&videoid=2095439', rnd = None):
		cherrypy.response.headers['Content-Type'] = 'application/json'
		return self._jsencoder.encode(get_streams(url))

	@cherrypy.expose
	def get_streams_xml(self, url = 'http://www.tv4play.se/sport/ekwall_vs_lundh?title=ekwall_vs_lundh_med_may_mahlangu&videoid=2095439', rnd = None):
		cherrypy.response.headers['Content-Type'] = 'application/xml'
		
		return self._render_template(template_name = 'get_streams.xml',
									args = dict(streams = [s.to_dict()
											for s in get_streams(url)]),
									type = 'xml')
	
	@cherrypy.expose
	def get_streams_old_xml(self, url = 'http://www.tv4play.se/sport/ekwall_vs_lundh?title=ekwall_vs_lundh_med_may_mahlangu&videoid=2095439', rnd = None):
		cherrypy.response.headers['Content-Type'] = 'application/xml'
		
		return self._render_template(template_name = 'get_streams_old.xml',
									args = dict(streams = [s.to_dict()
											for s in get_streams(url)]),
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
			return services
		else:
			return [s for s in services if s.title.lower() in titles]
	
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
	def index_html(self):
		return self._render_template(template_name = 'index.html')
	
	@cherrypy.expose
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
		qna_txt = open('qna.txt', 'r')
		qna = dict([pair.split('<!-- inner_delim -->') for pair in qna_txt.read().decode('utf-8').split('<!-- delim -->')])
		qna = dict([(Markup(q.strip()), Markup(a.strip())) for q, a in qna.items()])
		
		return self._render_template(template_name = 'qna.html', args = {'qna': qna})
	
	def _unfinished_factory():
		@cherrypy.expose
		def unfinished(self):
			return self._render_template(template_name = 'unfinished.html')
		return unfinished
	
	player_html = _unfinished_factory()

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
	global get_streams, services
	from lib.main import get_streams, services
	
	_config['/']['tools.staticdir.root'] = base_dir
	cherrypy.tree.mount(Root(template_dir = base_dir + '/templates'), config = _config, script_name = environ.get('pirateplay_script_name', ''))
	return cherrypy.tree(environ, start_response)

if __name__ == "__main__":
	from lib.main import get_streams, services
	
	from os import getcwd
	base_dir = getcwd()
	
	_config['global']['server.socket_port'] = 8081
	_config['/']['tools.staticdir.root'] = base_dir
	cherrypy.quickstart(Root(template_dir = base_dir + '/templates'), config = _config, script_name='/pirateplay2')