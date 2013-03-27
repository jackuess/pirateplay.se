# -*- encoding: UTF-8 -*-

import cherrypy

SESSION_KEY = '_cp_is_admin'

def check_auth(*args, **kwargs):
	import urllib
	
	require_admin = cherrypy.request.config.get('auth.require_admin', False)
	if require_admin:
		is_admin = cherrypy.session.get(SESSION_KEY)
		if not (is_admin == True):
			raise cherrypy.HTTPRedirect("authenticate/login.html?from_page=%s" % urllib.quote(cherrypy.request.request_line.split()[1]))
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def only_for_admin(f):
	if not hasattr(f, '_cp_config'):
		f._cp_config = dict()
	if 'auth.require_admin' not in f._cp_config:
		f._cp_config['auth.require_admin'] = True
	return f

class AuthController(object):
	@cherrypy.expose
	@cherrypy.tools.genshi_template(filename='login.html')
	def login_html(self, password=None, from_page="/"):
		from hashlib import sha256
		
		if password is None:
			return { 'msg': None, 'from_page': from_page }
        
		if sha256(password).hexdigest() != cherrypy.request.app.config['Pirateplay']['admin_password']:
			return { 'msg': u'Fel lösenord!', 'from_page': from_page }
		else:
			cherrypy.session[SESSION_KEY] = True
			raise cherrypy.HTTPRedirect(from_page or "/")
    
	@cherrypy.expose
	def logout_html(self, from_page="/"):
		cherrypy.session[SESSION_KEY] = None
		raise cherrypy.HTTPRedirect(from_page or "/")