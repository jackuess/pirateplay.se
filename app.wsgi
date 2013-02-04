# -*- coding: utf-8 -*-

import cherrypy, os, os.path, sys

sys.stdout = sys.stderr

#We can't do all imports before we know that cwd is properly set
def do_imports():
	global genshi_tool, Root
	import lib.genshi_tool as genshi_tool
	cherrypy.tools.genshi_template = cherrypy.Tool('before_handler', genshi_tool.GenshiLoader())
	from lib.root import Root

def wsgi_application(environ, start_response):
	base_dir = environ.get('pirateplay_base_dir', '')
	os.chdir(base_dir)
	
	if not base_dir in sys.path:
		sys.path.insert(0, base_dir)
	
	do_imports()
	
	cherrypy.config.update('config.ini')
	
	confdict = { }
	cherrypy.config.update(confdict)
	
	app = cherrypy.tree.mount(Root(), '', 'config.ini')
	app.merge(confdict)
	
	return cherrypy.tree(environ, start_response)

application = wsgi_application

if __name__ == "__main__":
	do_imports()
	
	cherrypy.config.update('config.ini')
	
	confdict = { 'global': { 'server.socket_port': 8081,
				'request.show_tracebacks': True,
				'tools.genshi_template.auto_reload': True,
				'log.screen': True } }
	cherrypy.config.update(confdict)
	
	app = cherrypy.tree.mount(Root(), '', 'config.ini')
	app.merge(confdict)

	if hasattr(cherrypy.engine, "signal_handler"):
		cherrypy.engine.signal_handler.subscribe()
	if hasattr(cherrypy.engine, "console_control_handler"):
		cherrypy.engine.console_control_handler.subscribe()
	
	cherrypy.engine.start()
	cherrypy.engine.block()