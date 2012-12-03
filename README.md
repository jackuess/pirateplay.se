# Pirateplay.se #
The entire code for running [Pirateplay.se](http://pirateplay.se)

Pirateplay.se can either be run as a WSGI application under ie. [mod_wsgi](http://code.google.com/p/modwsgi/), or
as a stand alone webserver in it self ([cherrypy.quickstart](http://docs.cherrypy.org/dev/refman/cherrypy.html#cherrypy.quickstart)).

## Dependencies ##
* [Python>=2.6](http://python.org/)
* [CherryPy](http://cherrypy.org/)
* [Genshi](http://genshi.edgewall.org/)

### Optional dependencies: ###
[PyAMF](http://www.pyamf.org/): for getting some streams from Brightcove

## Installation notices ##
config.ini must be present in root - a copy of config.ini.example should work
in most cases. If run under mod_wsgi: directory must be set via .htaccess - see
.htaccess.example.
