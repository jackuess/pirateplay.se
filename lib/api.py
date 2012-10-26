# -*- coding: utf-8 -*-

import cherrypy
from copy import deepcopy

import pirateplay
import sitemap


def service_handler(*args, **kwargs):
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return pirateplay.js_encoder.encode(value)


class Api():
	def _convert_service_re(self, service):
		import re
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
	@sitemap.add_to_sitemap('0.5')
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
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/get_streams_old.xml', type='xml')
	def get_streams_old_xml(self, url, librtmp = '0', output_file = '-', parent_function = ''):
		streams = pirateplay.get_streams(url)
		
		if streams[0].url.startswith('rtmp') and librtmp == '0':
			return { 'streams': [{'url': pirateplay.rtmpdump_cmd(s.url, output_file), 'meta': s.metadict()} for s in streams] }
		elif '.m3u8' in streams[0].url:
			return { 'streams': [{ 'meta': { 'quality': u'Inkompatibel ström. Uppgradera Pirateplayer.' }, 'url': 'http://localhost/' }] }
		elif 'manifest.f4m' in streams[0].url:
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