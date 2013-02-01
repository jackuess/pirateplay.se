# -*- coding: utf-8 -*-

import cherrypy
from genshi.core import Markup

import pirateplay, sitemap
from api import Api
from pirateplayer_downloader import PirateplayerDownloader

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
		
def format_tweet(s):
	import re
	s = re.sub(r'(https?://\S+)', '<a href="\\1">\\1</a>', s, flags=re.IGNORECASE)
	return re.sub(r'(@([^\s]+))', '<a href="http://twitter.com/\\2">\\1</a>', s, flags=re.IGNORECASE)

def send_mail(sender, recipient, subject, message, message_type):
	import smtplib
	from email.mime.text import MIMEText
	from email.utils import formatdate
	
	msg = MIMEText(message, message_type)
	msg['Date'] = formatdate()
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = recipient
	
	s = smtplib.SMTP('mail.wrutschkow.org')
	s.sendmail(sender, [recipient], msg.as_string())
	s.quit()

def handle_error():
	msg = '<h2>URL</h2><p><a href="%(url)s">%(url)s</a></p><h2>Traceback</h2><pre><code>%(traceback)s</code></pre>' % { 'url': cherrypy.url(qs=cherrypy.request.query_string),
																															'traceback': cherrypy._cperror.format_exc() }
	send_mail('error@pirateplay.se', 'jacques@pirateplay.se', 'Feil!', msg, 'html')
	
	cherrypy.response.status = 500
	cherrypy.response.body = ["<html><body>Sorry, an error occured</body></html>"]

def handle_error_404(status, message, traceback, version):
	from urllib import quote
	from genshi.template import TemplateLoader, Context
	
	template_loader = TemplateLoader(cherrypy.config.get('tools.genshi_template.dir'))
	template = template_loader.load('notfound.html')
	context = Context(url=cherrypy.url, quote=quote)
	stream = template.generate(context)
	
	return stream.render('xhtml')

class Root():
	_cp_config = { 'request.error_response': handle_error,
					'error_page.404': handle_error_404 }
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='sitemap.xml', type='xml')
	def sitemap_xml(self):
		return { 'sites': sitemap.sitemap }
	
	@cherrypy.expose
	def sitemap_html(self):
		return '<br />'.join(['<a href="%s">%s</a>' % ((i,)*2)
							for i in sitemap])
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='index.html')
	@sitemap.add_to_sitemap('1.0')
	def index(self):
		import datetime, twitter
		
		now = datetime.datetime.now()
		api = twitter.Api()
		try:
			tweets = api.GetUserTimeline('pirateplay_se', count=200)
				
			twitter = [{ 'text':  Markup(format_tweet(t.text)),
						'time': relative_time((now - datetime.datetime.strptime(t.created_at, '%a %b %d %H:%M:%S +0000 %Y')).total_seconds()) }
						for t in tweets
						if not t.text.startswith('@')]
		except (AttributeError, twitter.TwitterError):
			twitter = []
		
		services_se = sorted([s.to_dict() for s in pirateplay.services if len(s.items) > 0 and '\.se/' in s.items[0].re and s.title != ''], key=lambda s: s['title'])
		services_other = sorted([s.to_dict() for s in pirateplay.services if len(s.items) > 0 and not '\.se/' in s.items[0].re and s.title != ''], key=lambda s: s['title'])
		
		return dict(services_se = services_se, services_other = services_other, tweets = twitter)
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='app.html')
	def app_html(self):
		return  {}
	
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='library.html')
	def library_html(self):
		return {}
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='hls_guide.html')
	def hls_guide_html(self):
		return {}
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='hds_guide.html')
	def hds_guide_html(self):
		return {}
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='qna.html')
	def qna_html(self):
		qna_txt = open('data/qna.txt', 'r')
		qna = dict([pair.split('<!-- inner_delim -->') for pair in qna_txt.read().decode('utf-8').split('<!-- delim -->')])
		qna = dict([(Markup(q.strip()), Markup(a.strip())) for q, a in qna.items()])
		
		return {'qna': qna}
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.8')
	@cherrypy.tools.genshi_template(filename='player.html')
	def player_html(self):
		return dict(services = sorted([s.to_dict() for s in pirateplay.services if s.title != ''], key=lambda s: s['title']))
	
	#@cherrypy.expose
	#@sitemap.add_to_sitemap('0.2')
	#@cherrypy.tools.genshi_template(filename='osxbrev_2013-01-14.html')
	#def osxbrev_2013_01_14_html(self):
	#	return {}
	
	api = Api()
	pirateplayer_downloads = PirateplayerDownloader()
	generate_application_xml = api.get_streams_old_xml