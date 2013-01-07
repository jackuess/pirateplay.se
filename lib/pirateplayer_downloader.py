import cherrypy, os
import sitemap

logfile = 'data/pirateplayer_downloads.log'
archive_dir = 'static/pirateplayer_archive'

class PirateplayerDownloader():
	def downloads_dict(self):
		downloadlog_file = open(logfile, 'r')
		downloadlog = dict([entry.split() for entry in downloadlog_file])
		downloadlog_file.close()
		return downloadlog
		
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='pirateplayer_downloads.html')
	def index(self):
		downloads = sorted(self.downloads_dict().items())
		
		total_count = sum(int(d[1]) for d in downloads)
		
		return { 'downloads': downloads,
				'total_count': total_count }
	
	@cherrypy.expose
	def default(self, *args, **kwargs):
		filename = args[0]
		path = os.path.join(archive_dir, filename)
		
		if os.path.exists(path):
			downloadlog = self.downloads_dict()
			downloadlog[filename] = str(int(downloadlog.get(filename, '0')) + 1)
			
			downloadlog_file = open(logfile, 'w')
			
			for fn, count in sorted(downloadlog.items()):
				downloadlog_file.write(fn + ' ' + count + '\n')
			
			downloadlog_file.close()
			raise cherrypy.InternalRedirect(os.path.join('../', path))
		else:
			raise cherrypy.NotFound()
	
	def redirect_to_latest(self, ext):
		filenames = sorted(self.downloads_dict().keys())
		for name in filenames:
			if name.endswith(ext):
				latest = name
		
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