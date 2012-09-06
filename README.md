# Pirateplay.se #
The entire code for running [Pirateplay.se](http://pirateplay.se)

Pirateplay.se can either be run as a WSGI application under ie. mod_wsgi, or
as a stand alone webserver in it self (cherrypy.quickstart).

## Dependencies ##
* [Python>=2.6](http://python.org/)
* [CherryPy](http://cherrypy.org/)
* [Genshi](http://genshi.edgewall.org/)

### Optional dependencies: ###
PyAMF: for getting some streams from Brightcove

## Installation notices ##
config.ini must be present in root - a copy of config.ini.example should work
in most cases. If run under mod_wsgi: directory must be set via .htaccess - see
.htaccess.example.
