import cherrypy, os, sqlite3
import sitemap

#
# CREATE TABLE pirateplayer_downloads
# (id INTEGER PRIMARY KEY, filename TEXT, downloadcount INTEGER)
#
# CREATE UNIQUE INDEX name_idx
# ON pirateplayer_downloads(filename)
#

logfile = 'data/pirateplayer_downloads.log'
archive_dir = 'static/pirateplayer_archive'

class PirateplayerDownloader():
	def db_conn(self):
		conn = sqlite3.connect('data/db.lite')
		cursor = conn.cursor()
		return conn, cursor
		
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='pirateplayer_downloads.html')
	def index(self):
		conn, c = self.db_conn()
		
		c.execute('''SELECT filename, downloadcount
				FROM pirateplayer_downloads
				ORDER BY filename ASC''')
		downloads = c.fetchall()
		
		c.execute('''SELECT SUM(downloadcount)
				FROM pirateplayer_downloads''')
		total_count = c.fetchone()
		
		conn.close()
		
		return { 'downloads': downloads,
				'total_count': total_count }
	
	@cherrypy.expose
	def default(self, *args, **kwargs):
		filename = args[0]
		path = os.path.join(archive_dir, filename)
		
		if os.path.exists(path):
			conn, c = self.db_conn()
			c.execute('''INSERT OR REPLACE
					INTO pirateplayer_downloads(filename, downloadcount)
					VALUES ('%(filename)s', coalesce((select downloadcount from pirateplayer_downloads where filename = '%(filename)s'), 0)+1)''' % { 'filename': filename })
			conn.commit()
			conn.close()
			
			raise cherrypy.InternalRedirect(os.path.join('../', path))
		else:
			raise cherrypy.NotFound()
	
	def redirect_to_latest(self, ext):
		conn, c = self.db_conn()
		
		c.execute("""SELECT MAX(filename)
				FROM pirateplayer_downloads
				WHERE filename like '%%%s'""" % ext)
		latest = c.fetchone()
		
		conn.close()
		
		try:
			raise cherrypy.HTTPRedirect(latest)
		except UnboundLocalError:
			raise cherrypy.NotFound()
	
	@cherrypy.expose
	def latest_deb(self):
		self.redirect_to_latest(ext='.deb')
	
	@cherrypy.expose
	def latest_osx(self):
		self.redirect_to_latest(ext='.dmg')
	
	@cherrypy.expose
	def latest_win32(self):
		self.redirect_to_latest(ext='.exe')