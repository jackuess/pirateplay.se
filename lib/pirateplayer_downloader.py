## -*- coding: utf-8 -*-

import cherrypy, os, sqlite3
import sitemap
from urlparse import urljoin
from urllib import quote_plus
from urllib2 import urlopen, HTTPError

import auth

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
		
	def delete_download(self, id):
		self.cursor.execute("DELETE FROM pirateplayer_downloads WHERE id = '%s';" % id)
		self.conn.commit()
		
	def update_download(self, id, filename):
		self.cursor.execute('''UPDATE pirateplayer_downloads
							SET filename = '%s'
							WHERE id = '%s';''' % (filename, id))
		self.conn.commit()
	
	def get_downloads(self):
		try:
			self.cursor.execute('''SELECT filename, downloadcount, id
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
	_cp_config = {
		'tools.sessions.on': True,
		'tools.auth.on': True
	}
	
	authenticate = auth.AuthController()
	
	def archive_path(self, fn):
		return cherrypy.url(urljoin('/static/pirateplayer_archive/', fn))

	def return_message(self, msg, msg_type='success'):
		raise cherrypy.HTTPRedirect('manage.html?msg=%s&msg_type=%s' % (quote_plus(msg), msg_type))
	
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='pirateplayer_downloads.html')
	def index(self):
		db = Db()
		downloads, total_count = db.get_downloads()
		
		return { 'downloads': downloads,
				'total_count': total_count }
	
	@cherrypy.expose
	@auth.only_for_admin
	@cherrypy.tools.genshi_template(filename='pirateplayer/downloads/manage.html')
	def manage_html(self, msg=None, msg_type=None):
		db = Db()
		downloads, total_count = db.get_downloads()
		
		return { 'msg': msg, 'msg_type': msg_type,
				'downloads': downloads,
				'total_count': total_count }
		
	@cherrypy.expose
	@auth.only_for_admin
	def delete_html(self, filename, id):
		db = Db()
		try:
			db.delete_download(id)
			message = '%s borttagen!' % filename
			message_type = 'success'
		except sqlite3.OperationalError:
			message = '%s kunde inte tas bort!' % filename
			message_type = 'error'
			
		self.return_message(message, message_type)
	
	@cherrypy.expose
	@auth.only_for_admin
	def add_html(self, filename):	
		db = Db()
		msg_type = 'error'
		try:
			urlopen(self.archive_path(filename))
			db.add_download(filename)
			msg = u'Lade till nedladdning: %s!' % filename
			msg_type = 'success'
		except HTTPError:
			msg = u'Kunder inte lägga till nedladdning: %s, filen existerar inte!' % filename
		except sqlite3.OperationalError:
			msg = u'Kunder inte lägga till nedladdning: %s, databasfel!' % filename
			
		self.return_message(msg, msg_type)	
		
	@cherrypy.expose
	@auth.only_for_admin
	def update_html(self, filename, id):
		db = Db()
		msg_type='error'
		try:
			urlopen(self.archive_path(filename))
			db.update_download(id, filename)
			msg='%s uppdaterad!' % filename
			msg_type='success'
		except HTTPError:
			msg = 'Kunder inte uppdatera nedladdning: %s, filen existerar inte!' % filename
		except sqlite3.OperationalError:
			msg = u'Kunder inte uppdatera nedladdning: %s, databasfel!' % filename
			
		self.return_message(msg, msg_type)
	
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
