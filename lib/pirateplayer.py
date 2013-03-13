import cherrypy
import sitemap
import pirateplay
from pirateplayer_downloader import PirateplayerDownloader

class Pirateplayer():
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='pirateplayer/index.html')
	@sitemap.add_to_sitemap('0.8')
	def index(self):
		return dict(services = sorted([s for s in pirateplay.services if s.get('title', '') != ''], key=lambda s: s['title']))
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='pirateplayer/changelog.html')
	@sitemap.add_to_sitemap('0.5')
	def changelog_html(self):
		return {}
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='pirateplayer/get.html')
	@sitemap.add_to_sitemap('0.5')
	def get_html(self):
		return {}
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='pirateplayer/credits.html')
	@sitemap.add_to_sitemap('0.5')
	def credits_html(self):
		from json import load
		from urllib2 import urlopen
		
		flattrs = load(urlopen('https://api.flattr.com/rest/v2/things/361015/flattrs?count=999'))
		
		return { 'flattr_names': [(f['owner']['username'], f['owner']['link']) for f in flattrs] }
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='pirateplayer/screens.html')
	@sitemap.add_to_sitemap('0.5')
	def screens_html(self):
		return {}
	
	downloads = PirateplayerDownloader()