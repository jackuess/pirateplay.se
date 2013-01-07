import cherrypy, os
import sitemap

logfile = 'data/pirateplayer_downloads.log'

class PirateplayerDownloader():
	@cherrypy.expose
	@sitemap.add_to_sitemap('0.5')
	@cherrypy.tools.genshi_template(filename='pirateplayer_downloads.html')
	def index(self):
		total_count = 0
		out = '<table>'
		downloadlog = open(logfile, 'r')
		
		#for entry in downloadlog:
			#fn, count = entry.split()
			#total_count += int(count)
			#out += '<tr><td><a href="%s">%s</a></td><td>%s</td></tr>' % (fn, fn, count)
		downloads = [entry.split() for entry in downloadlog]
		
		for d in downloads:
			total_count += int(d[1])
		
		downloadlog.close()
		
		return { 'downloads': downloads,
				'total_count': total_count }
	
	@cherrypy.expose
	def default(self, *args, **kwargs):
		filename = args[0]
		path = os.path.join('static/pirateplayer_archive', filename)
		
		if os.path.exists(path):
			downloadlog_file = open(logfile, 'r')
			downloadlog = dict([entry.split() for entry in downloadlog_file])
			downloadlog_file.close()
			downloadlog[filename] = str(int(downloadlog.get(filename, '0')) + 1)
			
			downloadlog_file = open(logfile, 'w')
			
			for fn, count in sorted(downloadlog.items()):
				downloadlog_file.write(fn + ' ' + count + '\n')
			
			downloadlog_file.close()
			raise cherrypy.InternalRedirect(os.path.join('../', path))
		else:
			raise cherrypy.NotFound()