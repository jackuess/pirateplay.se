from lib.pirateplay.rerequest2 import TemplateRequest

try:
	from pyamf import remoting
	
	def brightcovedata(video_player, player_id, publisher_id, const):
		env = remoting.Envelope(amfVersion=3)
		env.bodies.append(
			(
				"/1", 
				remoting.Request(
					target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", 
					body=[const, player_id, video_player, publisher_id],
					envelope=env
				)
			)
		)
		return str(remoting.encode(env).read())

	def decode_bc(content):
		if content == '':
			return ''
		
		return ''.join(['"%sx%s:%s";' % (rendition['frameWidth'], rendition['frameHeight'], rendition['defaultURL'])
						for rendition in remoting.decode(content).bodies[0][1].body['renditions']])

except ImportError:
	print 'PyAMF not found! Brightcove support dissabled!'
	def brightcovedata(video_player, player_id, publisher_id, const):
		pass
	def decode_bc(content):
		pass


services = [{ 'title': 'Kanal9-play', 'url': 'http://kanal9play.se/', 'feed_url': 'http://www.kanal9play.se/rss?type=PROGRAM',
				'items': [TemplateRequest(
							re = r'(http://)?(www\.)?kanal9play\.se/(?P<req_url>.+)',
							encode_vars = lambda v: { 'req_url': 'http://kanal9play.se/%(req_url)s' % v } ),
						TemplateRequest(
							re = r'@videoPlayer" value="(?P<video_player>[^"]+)"',
							encode_vars = lambda v: { 'req_url': 'http://c.brightcove.com/services/messagebroker/amf?playerKey=AQ~~,AAAABUmivxk~,SnCsFJuhbr0vfwrPJJSL03znlhz-e9bk',
													'req_headers': { 'Content-type': 'application/x-amf' },
													'req_data': brightcovedata(v['video_player'], 811317479001, 22710239001, '9f79dd85c3703b8674de883265d8c9e606360c2e') } ),
						TemplateRequest(
							decode_content = decode_bc,
							re = r'"(?P<quality>\d+x\d+):(?P<final_url>[^&]+)&(?P<path>[^"]+)";',
							encode_vars = lambda v: { 'final_url': '%(final_url)s swfVfy=1 swfUrl=http://admin.brightcove.com/viewer/us1.25.04.01.2011-05-24182704/connection/ExternalConnection_2.swf playpath=%(path)s' % v,
													'suffix-hint': 'flv' } )] }]