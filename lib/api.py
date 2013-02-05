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
		if 'items' in s:
			try:
				s['test'] = re.sub(r'(\(\?P<\w+>)|(\(\?:)', '(', service['items'][0].re)
			except IndexError:
				pass
			del s['items']
		return s
		
	def _filter_services(self, titles):
		try:
			titles = [t.lower() for t in titles.split(',')]
		except AttributeError:
			return [s for s in pirateplay.services if 'title' in s]
		else:
			return [s for s in pirateplay.services if s.get('title', '').lower() in titles]
		
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='api/manual.html')
	def manual_html(self):
		return {}
	
	@cherrypy.expose
	@cherrypy.tools.json_out()
	def get_streams_js(self, url, rnd = None):
		return [{ 'url': s['final_url'],
				'meta': { 'quality': s.get('quality'),
						'subtitles': s.get('subtitles'),
						'suffixHint': s.get('suffix-hint'),
						'rtmpDumpRealtime': s.get('rtmpdump-realtime', False),
						'requiredPlayerVersion': s.get('required-player-version', '0') } } for s in pirateplay.get_streams(url)]

	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/get_streams.xml', type='xml')
	def get_streams_xml(self, url, rnd = None):
		url = url.encode('utf-8')
		return { 'streams': pirateplay.get_streams(url) }
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/get_streams_old.xml', type='xml')
	def get_streams_old_xml(self, url, librtmp = '0', output_file = '-', parent_function = ''):
		streams = pirateplay.get_streams(url)
		
		try:
			if streams[0]['final_url'].startswith('rtmp') and librtmp == '0':
				return { 'streams': [{'url': pirateplay.rtmpdump_cmd(s['final_url'], output_file), 'meta': s} for s in streams] }
			elif '.m3u8' in streams[0]['final_url']:
				return { 'streams': [{ 'meta': { 'quality': u'Inkompatibel ström. Uppgradera Pirateplayer.' }, 'url': 'http://localhost/' }] }
			elif 'manifest.f4m' in streams[0]['final_url']:
				return { 'streams': [{ 'meta': { 'quality': u'Inkompatibel ström. Testa appen på Pirateplay.se.' }, 'url': 'http://localhost/' }] }
			else:
				return { 'streams': [{'url': s['final_url'], 'meta': s} for s in streams] }
		except (IndexError, KeyError):
			return { 'streams': [] }
	
	@cherrypy.expose
	@cherrypy.tools.json_out(handler = service_handler)
	def services_js(self, titles = None, rnd = ''):
		s = self._filter_services(titles)
		return [self._convert_service_re(z) for z in s]

	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='api/services.xml', type='xml')
	def services_xml(self, titles = None, rnd = ''):
		return { 'services': self._filter_services(titles) }
