## -*- coding: utf-8 -*-

import cherrypy, os, sqlite3
import sitemap
from urlparse import urljoin

##
## CREATE TABLE pirateplayer_downloads
## (id INTEGER PRIMARY KEY, filename TEXT, downloadcount INTEGER)
##
## CREATE UNIQUE INDEX name_idx
## ON pirateplayer_downloads(filename)
##

class Db():
	def __init__(self):
		self.conn = sqlite3.connect('data/db.lite')
		self.cursor = self.conn.cursor()
		#pass
	
	def __del__(self):
		self.cursor.close()
		self.conn.close()
	
	def create_table(self):
		self.cursor.execute('''CREATE TABLE pirateplayer_downloads
								(id INTEGER PRIMARY KEY, filename TEXT, downloadcount INTEGER);''')
		self.cursor.execute('''CREATE UNIQUE INDEX name_idx
								ON pirateplayer_downloads(filename);''')
		self.conn.commit()
	
	def add_download(self, filename):
		self.cursor.execute('''INSERT INTO pirateplayer_downloads(filename, downloadcount)
							VALUES('%s', 0);''' % filename)
		self.conn.commit()
	
	def get_downloads(self):
		try:
			self.cursor.execute('''SELECT filename, downloadcount
						FROM pirateplayer_downloads
						ORDER BY filename ASC;''')
			downloads = self.cursor.fetchall()
		except sqlite3.OperationalError as e:
			self.create_table()
			downloads = []
		
		self.cursor.execute('''SELECT SUM(downloadcount)
				FROM pirateplayer_downloads;''')
		total_count = self.cursor.fetchone()
		
		return downloads, total_count
	
	def increase_download_count(self, filename):
		self.cursor.execute('''UPDATE pirateplayer_downloads
				SET downloadcount=(select downloadcount from pirateplayer_downloads where filename = '%(filename)s')+1
				WHERE filename='%(filename)s';''' % { 'filename': filename })
		self.conn.commit()
	
	def get_latest_by_extension(self, ext):
		try:
			self.cursor.execute("""SELECT MAX(filename)
						FROM pirateplayer_downloads
						WHERE filename like '%%%s';""" % ext)
			return self.cursor.fetchone()
		except sqlite3.OperationalError:
			self.create_table()
			return (None,)

class PirateplayerDownloader():
	def archive_path(self, fn):
		return cherrypy.url(urljoin('/static/pirateplayer_archive/', fn))
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='pirateplayer_downloads.html')
	def index(self):
		db = Db()
		downloads, total_count = db.get_downloads()
		
		return { 'downloads': downloads,
				'total_count': total_count }
	
	@cherrypy.expose
	def default(self, *args, **kwargs):
		filename = '/'.join(args)
		db = Db()
		
		db.increase_download_count(filename)
		
		raise cherrypy.HTTPRedirect(self.archive_path(filename))
	
	def redirect_to_latest(self, ext):
		db = Db()
		latest = db.get_latest_by_extension(ext)
			
		if latest == (None,):
			raise cherrypy.NotFound()
		else:
			raise cherrypy.HTTPRedirect(latest)
	
	@cherrypy.expose
	def latest_osx(self):
		self.redirect_to_latest(ext='.dmg')
	
	@cherrypy.expose
	def latest_win32(self):
		self.redirect_to_latest(ext='.exe')
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='add_pirateplayer_download_form.html')
	def add_download_html(self):
		return {}
	
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='add_pirateplayer_download.html')
	def add_download_result_html(self, filename, password):
		from hashlib import sha256
		from urllib2 import urlopen, HTTPError
		db = Db()
	
		if sha256(password).hexdigest() != cherrypy.request.app.config['Pirateplay']['admin_password']:
			return { 'messages': [{ 'message': u'Fel lösenord!',
									'success': False }] }
		else:
			try:
				urlopen(self.archive_path(filename))
				db.add_download(filename)
				return { 'messages': [{ 'message': u'Lade till nedladdning: %s!' % filename,
										'success': True }] }
			except HTTPError:
				return { 'messages': [{ 'message': u'Kunder inte lägga till nedladdning: %s, filen existerar inte!' % filename,
										'success': False }] }
