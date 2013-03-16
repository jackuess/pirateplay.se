import cherrypy
from urllib2 import urlopen
import sitemap
import pirateplay
from pirateplayer_downloader import PirateplayerDownloader

def github_latest_version(username, repository):
	import json
	tags = json.load(urlopen('https://api.github.com/repos/%s/%s/tags' % (username, repository)))
	return sorted(tags, key = lambda t: t.get('name', 'v0').split('.'))[-1].get('name', 'v0')

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
		import markdown
		from genshi.core import Markup
		username = 'jackuess'
		repository = 'pirateplayer'
		tag = github_latest_version(username, repository)
		md = unicode(urlopen('https://raw.github.com/%s/%s/%s/CHANGELOG.md' % (username, repository, tag)).read(), 'utf-8')
		return { 'changelog_markup': Markup(markdown.markdown(md)) }
	
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
		
		flattrs = load(urlopen('https://api.flattr.com/rest/v2/things/361015/flattrs?count=999'))
		
		return { 'flattr_names': [(f['owner']['username'], f['owner']['link']) for f in flattrs] }
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='pirateplayer/screens.html')
	@sitemap.add_to_sitemap('0.5')
	def screens_html(self):
		from os import listdir
		
		def create_description(img):
			img = img.replace('.png', '')
			img = img.replace('_', '.')
			img = img.replace('x', '')
			return img.replace('-', ' ')
		
		screen_dir = 'static/images/ppscreens/'
		screens = sorted([{ 'thumb_link': cherrypy.url('../' + screen_dir + img.replace('.png', '.thumb.png')),
						'link': cherrypy.url('../' + screen_dir + img),
						'description': create_description(img) }
					for img in listdir('static/images/ppscreens/')
					if img.endswith('.png') and not img.endswith('.thumb.png')], reverse=True)
		
		return { 'screens': screens }
	
	downloads = PirateplayerDownloader()