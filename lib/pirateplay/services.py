from urllib import unquote
from urllib2 import HTTPRedirectHandler, urlopen
from random import randint

from rerequest import RequestChain, TemplateRequest

def fix_playpath(url):
	return url.replace('/mp4:', '/ playpath=mp4:')	

def remove_nullsubs(v):
	if urlopen(v['id']).read() == '':
			v['sub'] = ''
	return v

def add_subs_kanal5(v):
	suburl = 'http://www.kanal5play.se/api/subtitles/' + v['id']
	if urlopen(suburl).read() != '[]':
		v['sub'] = suburl
	return v

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
		r = ''
		for rendition in remoting.decode(content).bodies[0][1].body['renditions']:
			r += '"%sx%s:%s";' % (rendition['frameWidth'], rendition['frameHeight'], rendition['defaultURL'])
		return r

except ImportError:
	print 'PyAMF not found! Brightcove support dissabled!'
	def brightcovedata(video_player, player_id, publisher_id, const):
		pass
	def decode_bc(content):
		pass

from cStringIO import StringIO
class redirect_handler(HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		return StringIO(str(headers))


svtplay = RequestChain(title = 'SVT-play', url = 'http://svtplay.se/',
				items = [TemplateRequest(
							re = r'^(http://)?(www\.)?svtplay\.se/(?P<path>.*)',
							url_template = 'http://svtplay.se/%(path)s?type=embed&output=json'),
						TemplateRequest(
							re = r'"url":"(?P<url>rtmp[^"]+)".*?"bitrate":(?P<bitrate>\d+)(?=.*?"subtitleReferences":\[{"url":"(?P<sub>[^"]*))',
							url_template = '%(url)s swfVfy=1 swfUrl=http://www.svtplay.se/public/swf/video/svtplayer-2012.15.swf',
							encode_vars = remove_nullsubs,
							meta_template = 'quality=%(bitrate)s kbps; subtitles=%(sub)s; suffix-hint=flv',
							is_last = True)])
svtplay_hls = RequestChain(
				items = [TemplateRequest(
							re = r'^(http://)?(www\.)?svtplay\.se/(?P<path>.*)',
							url_template = 'http://svtplay.se/%(path)s?type=embed&output=json'),
						TemplateRequest(
							re = r'"url":"(?P<url>http://[^"]+\.m3u8)".*?subtitleReferences":\[{"url":"(?P<sub>[^"]*)',
							url_template = '%(url)s'),
						TemplateRequest(
							re = r'RESOLUTION=(?P<resolution>\d+x\d+).*?(?P<url>http://[^\n]+)',
							url_template = '%(url)s',
							encode_vars = remove_nullsubs,
							meta_template = 'quality=%(resolution)s;subtitles=%(sub)s; suffix-hint=mp4',
							is_last = True)])
svtplay_hds = RequestChain(#Not enabled!
				items = [TemplateRequest(
							re = r'^(http://)?(www\.)?svtplay\.se/(?P<path>.*)',
							url_template = 'http://svtplay.se/%(path)s?type=embed&output=json'),
						TemplateRequest(
							re = r'"url":"(?P<url>http://[^"]+\.f4m)"',
							encode_vars = lambda v: { 'guid': ''.join(chr(65 + randint(0, 25)) for i in range(12)) },
							url_template = '%(url)s?hdcore=2.8.0&g=%(guid)s',
							meta_template = 'quality=dynamisk; suffix-hint=flv',
							is_last = True)])
svtplay_http = RequestChain(
				items = [TemplateRequest(
							re = r'^(http://)?(www\.)?svtplay\.se/(?P<path>.*)',
							url_template = 'http://svtplay.se/%(path)s?type=embed&output=json'),
						TemplateRequest(
							re = r'"url":"(?P<url>http://[^"]+)".*?"bitrate":(?P<bitrate>\d+)(?=.*?"subtitleReferences":\[{"url":"(?P<sub>[^"]*))',
							url_template = '%(url)s',
							meta_template = 'quality=%(bitrate)s; subtitles: %(sub)s',
							is_last = True)])

urplay = RequestChain(title = 'UR-play', url = 'http://urplay.se/', feed_url = 'http://urplay.se/rss-senasteprogram',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?urplay\.se/(?P<url>.+)',
							url_template = 'http://urplay.se/%(url)s'),
						TemplateRequest(
							re = r'file=/(?P<url>[^&]+(?P<ext>mp[34]))(?:.*?captions.file=(?P<sub>[^&]+))?',
							url_template = 'rtmp://streaming.ur.se/ playpath=%(ext)s:/%(url)s app=ondemand ',
							meta_template = 'subtitles=%(sub)s; suffix-hint=flv',
							is_last = True)])

sr = RequestChain(title = 'SR', url = 'http://sr.se/', feed_url = 'http://sverigesradio.se/api/rss/broadcast/516',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?sverigesradio\.se/(?P<url>.+)',
							url_template = 'http://sverigesradio.se/%(url)s'),
						TemplateRequest(
							re = r'<ref href="(?P<url>[^"]+)"',
							url_template = '%(url)s',
							meta_template = '',
							is_last = True)])

tv4play = RequestChain(title = 'TV4-play', url = 'http://tv4play.se/', feed_url = 'http://www.tv4play.se/rss/sport/ekwall_vs_lundh',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?tv4play\.se/.*(videoid|vid)=(?P<id>\d+).*',
							url_template = 'http://premium.tv4play.se/api/web/asset/%(id)s/play'),
						TemplateRequest(
							re = r'(<playbackStatus>(?P<status>\w+).*?)?<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?(?P<base>rtmpe?://[^<]+).*?(?P<url>mp4:/[^<]+)(?=.*?(?P<sub>http://((anytime)|(prima))\.tv4(play)?\.se/multimedia/vman/smiroot/[^<]+))?',
							url_template = '%(base)s playpath=%(url)s swfVfy=1 swfUrl=http://www.tv4play.se/flash/tv4playflashlets.swf',
							meta_template = 'quality=%(bitrate)s kbps; subtitles=%(sub)s; suffix-hint=flv',
							is_last = True)])
tv4play_hds = RequestChain(
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?tv4play\.se/.*(videoid|vid)=(?P<id>\d+).*',
							url_template = 'http://premium.tv4play.se/api/web/asset/%(id)s/play'),
						TemplateRequest(
							re = r'<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?<url>(?P<url>http://.*?\.mp4\.csmil/manifest\.f4m)</url>',
							url_template = '%(url)s?hdcore=2.7.6',
							meta_template = 'quality=%(bitrate)s kbps',
							is_last = True)])
tv4play_http = RequestChain(
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?tv4play\.se/.*(videoid|vid)=(?P<id>\d+).*',
							url_template = 'http://premium.tv4play.se/api/web/asset/%(id)s/play'),
						TemplateRequest(
							re = r'<url>(?P<url>http://[^<]+).*?(?=.*?(?P<sub>http://((anytime)|(prima))\.tv4(play)?\.se/multimedia/vman/smiroot/[^<]+))?',
							url_template = '%(url)s',
							meta_template = 'subtitles=%(sub)s',
							is_last = True)])
fotbollskanalen = RequestChain(title = 'Fotbollskanalen', url = 'http://fotbollskanalen.se/', sample_url = 'http://www.fotbollskanalen.se/video/?videoid=2194841',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?fotbollskanalen\.se/.*(videoid|vid)=(?P<id>\d+).*',
							url_template = 'http://premium.tv4play.se/api/web/asset/%(id)s/play'),
						TemplateRequest(
							re = r'(<playbackStatus>(?P<status>\w+).*?)?<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?(?P<base>rtmpe?://[^<]+).*?(?P<url>mp4:/[^<]+)(?=.*?(?P<sub>http://anytime.tv4.se/multimedia/vman/smiroot/[^<]+))?',
							url_template = '%(base)s swfVfy=1 swfUrl=http://www.tv4play.se/flash/tv4playflashlets.swf playpath=%(url)s',
							meta_template = 'quality=%(bitrate)s kbps; subtitles=%(sub)s; suffix-hint=flv',
							is_last = True)])


kanal5play = RequestChain(title = 'Kanal5-play', url = 'http://kanal5play.se/', feed_url = 'http://www.kanal5play.se/rss?type=PROGRAM',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?kanal5play\.se/.*video/(?P<id>\d+)',
							url_template = 'http://www.kanal5play.se/api/getVideo?format=FLASH&videoId=%(id)s'),
						TemplateRequest(
							re = r'"bitrate":(?P<bitrate>\d+).*?"source":"(?P<path>[^"]+)"(?=.*?"streamBaseUrl":"(?P<base>[^"]+)")',
							url_template = '%(base)s playpath=%(path)s swfVfy=1 swfUrl=http://www.kanal5play.se/flash/StandardPlayer.swf',
							meta_template = 'quality=%(bitrate)s; subtitles=%(sub)s; suffix-hint=flv',
							encode_vars = add_subs_kanal5,
							is_last = True)])

kanal9play = RequestChain(title = 'Kanal9-play', url = 'http://kanal9play.se/', feed_url = 'http://www.kanal9play.se/rss?type=PROGRAM',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?kanal9play\.se/(?P<url>.+)',
							url_template = 'http://kanal9play.se/%(url)s'),
						TemplateRequest(
							re = r'@videoPlayer" value="(?P<video_player>[^"]+)"',
							url_template = 'http://c.brightcove.com//services/messagebroker/amf?playerKey=AQ~~,AAAABUmivxk~,SnCsFJuhbr0vfwrPJJSL03znlhz-e9bk',
							headers = { 'Content-type': 'application/x-amf' },
							encode_vars = lambda match_vars: { 'bc_data': brightcovedata(match_vars['video_player'], 811317479001, 22710239001, '9f79dd85c3703b8674de883265d8c9e606360c2e') },
							data_template = '%(bc_data)s'),
						TemplateRequest(
							decode_content = decode_bc,
							re = r'"(?P<height>\d+)x(?P<width>\d+):(?P<URL>[^&]+)&(?P<path>[^"]+)";',
							url_template = '%(URL)s swfVfy=1 swfUrl=http://admin.brightcove.com/viewer/us1.25.04.01.2011-05-24182704/connection/ExternalConnection_2.swf playpath=%(path)s',
							meta_template = 'quality=%(height)sx%(width)s; suffix-hint=flv',
							is_last = True)])



tv3play = RequestChain(title = 'TV3-play', url = 'http://tv3play.se/',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?tv[368]play\.se/.*(?:play/(?P<id>\d+)).*',
							url_template = 'http://viastream.viasat.tv/PlayProduct/%(id)s'),
						TemplateRequest(
							re = r'<SamiFile>(?P<sub>[^<]*).*<Video>.*<BitRate>(?P<bitrate>\d+).*?<Url><!\[CDATA\[(?P<url>rtmp[^\]]+)',
							url_template = '%(url)s swfVfy=1 swfUrl=http://flvplayer.viastream.viasat.tv/play/swf/player120328.swf',
							meta_template = 'quality=%(bitrate)s kbps; subtitles=%(sub)s; suffix-hint=flv',
							decode_url = fix_playpath,
							is_last = True)])
mtg_alt = RequestChain(
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?tv[368]play\.se/.*(?:play/(?P<id>\d+)).*',
							url_template = 'http://viastream.viasat.tv/PlayProduct/%(id)s'),
						TemplateRequest(
							re = r'<SamiFile>(?P<sub>[^<]*).*<Video>.*<BitRate>(?P<bitrate>\d+).*?<Url><!\[CDATA\[(?P<url>http[^\]]+)',
							url_template = '%(url)s'),
						TemplateRequest(
							re = r'<Url>(?P<url>[^<]+)',
							url_template = '%(url)s swfVfy=1 swfUrl=http://flvplayer.viastream.viasat.tv/play/swf/player120328.swf',
							meta_template = 'quality=%(bitrate)s kbps; subtitles=%(sub)s; suffix-hint=flv',
							decode_url = fix_playpath,
							is_last = True)])
#Dummies: TV6-play and TV8-play is caught by tv3play and mtg_alt
tv6play = RequestChain(title = 'TV6-play', url = 'http://tv6play.se/', feed_url = 'http://www.tv6play.se/rss/mostviewed', items = [])
tv8play = RequestChain(title = 'TV8-play', url = 'http://tv8play.se/', feed_url = 'http://www.tv8play.se/rss/recent', items = [])

youtube = RequestChain(title = 'Youtube', url = 'http://youtube.com/', feed_url = 'http://gdata.youtube.com/feeds/base/videos?alt=rss',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?youtube\.com/(?P<url>.+)',
							url_template = 'http://youtube.com/%(url)s'),
						TemplateRequest(
							re = r'(url_encoded_fmt_stream_map=|%2C)url%3D(?P<url>.+?)%26quality%3D(?P<quality>.+?)%26',
							decode_url = lambda url: unquote(unquote(url)),
							url_template = '%(url)s',
							meta_template = 'quality=%(quality)s\n',
							is_last = True)])

vimeo = RequestChain(title = 'Vimeo', url = 'http://vimeo.com/', feed_url = 'http://vimeo.com/channels/staffpicks/videos/rss',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?vimeo\.com/.*?(?P<id>\d+)$',
							headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36'},
							url_template = 'http://vimeo.com/%(id)s'),
						TemplateRequest(
							re = r'"signature":"(?P<sig>[^"]+)".*?timestamp":(?P<time>\d+).*?((h264)|(vp6))":\["(?P<quality>[^"]+)',
							headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36'},
							url_template = 'http://player.vimeo.com/play_redirect?clip_id=%(id)s&sig=%(sig)s&time=%(time)s&quality=%(quality)s&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location=',
							handlerchain = redirect_handler()),
						TemplateRequest(
							re = r'Location: (?P<url>.*?)\s',
							headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36'},
							url_template = '%(url)s',
							meta_template = 'quality=%(quality)s',
							is_last = True)])


aftonbladet = RequestChain(title = 'Aftonbladet-TV', url = 'http://aftonbladet.se/', feed_url = 'http://www.aftonbladet.se/webbtv/rss.xml',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?aftonbladet\.se/(?P<url>.+)',
							url_template = 'http://aftonbladet.se/%(url)s'),
						TemplateRequest(
							re = r'playerWidth:\s(?P<width>\d+).*?playerHeight:\s(?P<height>\d+).*?videoUrl:\s"(?P<base>rtmp://([^/]+)/[^/]+/)(?P<url>[^"]+)".*?videoIsLive:\s(?P<live>true|false)',
							url_template = '%(base)s playpath=%(url)s live=%(live)s',
							decode_url = lambda url: url.replace('live=true', 'live=1').replace(' live=false', ''),
							meta_template = 'quality=%(width)sx%(height)s; suffix-hint=flv',
							is_last = True)])
aftonbladet_http = RequestChain(#title = 'Aftonbladet-TV', url = 'http://aftonbladet.se/',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?aftonbladet\.se/(?P<url>.+)',
							url_template = 'http://aftonbladet.se/%(url)s'),
						TemplateRequest(
							re = r'playerWidth:\s(?P<width>\d+).*?playerHeight:\s(?P<height>\d+).*?videoUrl:\s"(?P<url>[^"]+)"',
							url_template = '%(url)s',
							meta_template = 'quality=%(width)sx%(height)s',
							is_last = True)])

filmarkivet = RequestChain(title = 'Filmarkivet', url = 'http://filmarkivet.se/', sample_url = 'http://filmarkivet.se/sv/Film/?movieid=220',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?filmarkivet\.se/(?P<path>.*)',
							url_template = 'http://filmarkivet.se/%(path)s'),
						TemplateRequest(
							re = r"movieName\s=\s'(?P<movie_name>[^']+)'.*?streamer:\s'(?P<base>[^']+)'",
							url_template = '%(base)s%(movie_name)s',
							meta_template = '',
							is_last = True)])

elitserien_play = RequestChain(title = 'Elitserien-play', url = 'http://elitserienplay.se/',
				items = [TemplateRequest(
							re = r'(http://)?(www\.)?elitserienplay\.se/.*?video\.(?P<video_player>\d+)',
							url_template = 'http://c.brightcove.com//services/messagebroker/amf?playerKey=AQ~~,AAAAmNAkCuE~,RfA9vPhrJwdowytpDwHD00J5pjBMVHD6',
							headers = { 'Content-type': 'application/x-amf' },
							encode_vars = lambda match_vars: { 'bc_data': brightcovedata(match_vars['video_player'], 1199515803001, 656327052001, '2ba01fac60a902ffc3c6322c3ef5546dbcf393e4') },
							data_template = '%(bc_data)s'),
							#url_template = 'brightcove:video_player=%(video_player)s&player_id=1199515803001&publisher_id=656327052001&const=2ba01fac60a902ffc3c6322c3ef5546dbcf393e4&player_key=AQ~~,AAAAmNAkCuE~,RfA9vPhrJwdowytpDwHD00J5pjBMVHD6', is_last = True),
						TemplateRequest(
							decode_content = decode_bc,
							re = r'"(?P<height>\d+)x(?P<width>\d+):(?P<URL>[^&]+)&(?P<path>[^\?]+)(?P<query>\?[^"]+)";',
							url_template = '%(URL)s%(query)s swfVfy=1 swfUrl=http://admin.brightcove.com/viewer/us1.25.04.01.2011-05-24182704/connection/ExternalConnection_2.swf playpath=%(path)s',
							meta_template = 'quality=%(height)sx%(width)s; suffix-hint=flv',
							is_last = True)])

nrk = RequestChain(title = 'NRK nett-TV', url = 'http://nrk.no/nett-tv/',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?nrk+.no/nett-tv/(?P<url>.+)',
							headers = {'Cookie': 'NetTV2.0Speed=7336'},
							url_template = 'http://nrk.no/nett-tv/%(url)s'),
						TemplateRequest(
							re = r'name="Url" value="(?P<url>[^"]+)',
							url_template = '%(url)s'),
						TemplateRequest(
							re = r'href="(?P<url>mms://[^"]+)"',
							url_template = '%(url)s',
							meta_template = 'suffix-hint=wmv',
							is_last = True)])

dr = RequestChain(title = 'DR-TV', url = 'http://dr.dk/tv',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?dr\.dk/(?P<path>TV/se/.+)',
							url_template = 'http://www.dr.dk/%(path)s'),
						TemplateRequest(
							re = r'videoData:\s+{.+?resource:\s+"(?P<resource_url>[^"]+)"',
							url_template = '%(resource_url)s',
							handlerchain = redirect_handler()),
						TemplateRequest(
							re = r'Location: (?P<redirect_url>.*?)\n',
							url_template = '%(redirect_url)s'),
						TemplateRequest(
							re = r'"uri":"(?P<rtmp_base>rtmpe?:\\/\\/vod\.dr\.dk\\/cms\\/)(?P<rtmp_path>[^"]+).*?"bitrateKbps":(?P<bitrate>\d+)',
							decode_url = lambda url: url.replace('\\', ''),
							url_template = '%(rtmp_base)s playpath=%(rtmp_path)s swfVfy=1 swfUrl=http://www.dr.dk/assets/swf/program-player.swf',
							meta_template = 'quality=%(bitrate)s kbps; suffix-hint=flv',
							is_last = True)])

ceskatelevize = RequestChain(title = 'Ceskatelevize', url = '',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?ceskatelevize\.cz/(?P<url>.+)',
							url_template = 'http://www.ceskatelevize.cz/%(url)s', is_last = True),
						TemplateRequest(
							re = r'IDEC="(?P<identifier>[^"]+)"',
							data_template = 'options%%5BuserIP%%5D=85.226.8.253&options%%5BplayerType%%5D=flash&options%%5BplaylistItems%%5D%%5B0%%5D%%5BType%%5D=Ad&options%%5BplaylistItems%%5D%%5B0%%5D%%5BFormat%%5D=MP4_Web&options%%5BplaylistItems%%5D%%5B0%%5D%%5BIdentifier%%5D=AD-46&options%%5BplaylistItems%%5D%%5B0%%5D%%5BTitle%%5D=Reklama%%3A+Adventn%%C3%%AD+kalend%%C3%%A1%%C5%%99&options%%5BplaylistItems%%5D%%5B0%%5D%%5BSkip%%5D%%5BEnable%%5D=true&options%%5BplaylistItems%%5D%%5B0%%5D%%5BSkip%%5D%%5BDelay%%5D=3&options%%5BplaylistItems%%5D%%5B0%%5D%%5BClickThruURL%%5D=http%%3A%%2F%%2Fadvent.ceskatelevize.cz%%2F&options%%5BplaylistItems%%5D%%5B1%%5D%%5BType%%5D=Archive&options%%5BplaylistItems%%5D%%5B1%%5D%%5BFormat%%5D=MP4_Web&options%%5BplaylistItems%%5D%%5B1%%5D%%5BIdentifier%%5D=%(identifier)s&options%%5BplaylistItems%%5D%%5B1%%5D%%5BTitle%%5D=Vypr%%C3%%A1v%%C4%%9Bj&options%%5BplaylistItems%%5D%%5B1%%5D%%5BRegion%%5D=&options%%5BplaylistItems%%5D%%5B1%%5D%%5BSubtitlesUrl%%5D=http%%3A%%2F%%2Fimg7.ceskatelevize.cz%%\
2Fivysilani%%2Fsubtitles%%2F211%%2F211522161400013%%2Fsubtitles-1.txt&options%%5BplaylistItems%%5D%%5B1%%5D%%5BIndexes%%5D=null&options%%5BpreviewImageURL%%5D=http%%3A%%2F%%2Fimg7.ceskatelevize.cz%%2Fcache%%2F512x288%%2Fivysilani%%2Fepisodes%%2Fphotos%%2Fw512%%2F10195164142%%2F1-62384.jpg',
							url_template = 'http://www.ceskatelevize.cz/ajax/playlistURL.php'),
						TemplateRequest(
							re = r'(?P<playlist_url>.+)',
							headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0'},
							url_template = '%(playlist_url)s'),
						TemplateRequest(
							re = r'(base="(?P<base>rtmp://[^/]+/)(?P<app>[^"]+)".*?)?src="(?P<play_path>[^"]+)".*?label="(?P<quality>[^"]+)"',
							decode_url = lambda url: url.replace('&amp;', '&'),
							headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0'},
							url_template = '%(base)s app=%(app)s playpath=%(play_path)s swfVfy=1 swfUrl=http://img7.ceskatelevize.cz/libraries/player/flashPlayer.swf?version=1.44.5',
							meta_template = 'quality=%(quality)s; suffix-hint=flv',
							is_last = True)])

expressen = RequestChain(title = 'Expressen-TV', url = 'http://expressen.se/tv/',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?expressen\.se/(?P<path>.+)',
							url_template = 'http://www.expressen.se/%(path)s?'),
						TemplateRequest(
							re = r'swfobject.embedSWF\("(?P<swf_path>[^"]+)",\s"tvMainVideo".*?xmlUrl:\s\'(?P<xml_url>[^\']+)',
							url_template = '%(xml_url)s'),
						TemplateRequest(
							re = r'<vurl bitrate="(?P<bitrate>\d+)"><!\[CDATA\[(?P<base>rtmpe?://[^/]+/[^/]+)/(?P<play_path>[^\]]+)(\.flv)?',
							url_template = '%(base)s playpath=%(play_path)s swfVfy=1 swfUrl=http://www.expressen.se%(swf_path)s',
							meta_template = 'quality=%(bitrate)s; suffix-hint=flv',
							is_last = True)])

cnbc = RequestChain(title = 'CNBC', url = 'http://cnbc.com/',
				items = [ TemplateRequest(
							re = r'(http://)?((www|video)\.)?\.cnbc+.com/.*video=(?P<video>\d+).*',
							url_template = 'http://video.cnbc.com/gallery/?video=%(video)s'),
						TemplateRequest(
							re = r',formatLink:\'[^|]+\|(?P<xml_url>[^\']+)',
							url_template = '%(xml_url)s'),
						TemplateRequest(
							re = r'<choice>\s*<url>(?P<rtmp_url>rtm.+?)</url>',
							url_template = '%(rtmp_url)s; suffix-hint=flv',
							meta_template = '',
							is_last = True)])

discovery = RequestChain(title = 'Discovery', url = 'http://dsc.discovery.com/',
				items = [TemplateRequest(
							re = r'(http://)?dsc\.discovery\.com/(?P<path>.+)',
							url_template = 'http://dsc.discovery.com/%(path)s'),
						TemplateRequest(
							re = r'"clips":\s*\[\s*{\s*"clipRefId"\s*:\s*"(?P<id>[^"]+)"',
							url_template = 'http://static.discoverymedia.com/videos/components/dsc/%(id)s/smil-service.smil'),
						TemplateRequest(
							re = r'(<meta\s+name="httpBase"\s+content="(?P<base>[^"]+)".*?)?<video\s+src="(?P<path>[^"]+)"\s+system-bitrate="(?P<bitrate>\d+)"',
							url_template = '%(base)s/%(path)s',
							encode_vars = lambda d: { 'bitrate': str(int(d['bitrate'])/1000) },
							meta_template = 'quality=%(bitrate)s kbps; suffix-hint=flv', is_last = True)])

das_erste = RequestChain(title = 'Das Erste Mediathek', url = 'http://mediathek.daserste.de/',
				items = [ TemplateRequest(
							re = r'(http://)?mediathek\.daserste\.de/(?P<path>.*)',
							url_template = 'http://mediathek.daserste.de/%(path)s'),
						TemplateRequest(
							re = r'mediaCollection\.addMediaStream\(\d,\s(?P<quality>\d),\s"(?P<base>[^"]+)",\s"(?P<path>[^"]+)"',
							url_template = '%(base)s playpath=%(path)s',
							meta_template = 'quality=%(quality)s; suffix-hint=flv',
							is_last = True)])

disney_jr = RequestChain(title = 'Disney Junior', url = 'http://www.disney.se/disney-junior/innehall/video.jsp',
				items = [ TemplateRequest(
							re = r'(http://)?(www\.)?disney\.se/disney-junior/(?P<path>.+)',
							url_template = 'http://www.disney.se/disney-junior/%(path)s'),
						TemplateRequest(
							re = r"config\.firstVideoSource\s=\s'(?P<play_path>[^']+)'.*?config\.rtmpeServer\s=\s'(?P<base>[^']+)'",
							url_template = '%(base)s playpath=mp4:/%(play_path)s swfVfy=1 swfUrl=http://www.disney.se/cms_res/disney-junior/flash/video_hub_player/disney_player.swf',
							meta_template = 'suffix-hint=flv',
							is_last = True)])



services = [svtplay, svtplay_hls, svtplay_hds, svtplay_http,
			urplay,
			sr,
			tv3play, tv6play, tv8play, mtg_alt,
			tv4play, tv4play_hds, tv4play_http, fotbollskanalen,
			kanal5play,
			kanal9play,
			youtube,
			vimeo,
			aftonbladet, aftonbladet_http,
			filmarkivet,
			elitserien_play,
			nrk,
			dr,
			#ceskatelevize,
			expressen,
			cnbc,
			discovery,
			das_erste,
			disney_jr]