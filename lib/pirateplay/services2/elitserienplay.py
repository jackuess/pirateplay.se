# -*- coding: utf-8 -*-

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

services = [{ 'title': 'Elitserien-play', 'url': 'http://elitserienplay.se/',
				'items': [TemplateRequest(
							re = r'(http://)?(www\.)?elitserienplay\.se/.*?video\.(?P<video_player>\d+)',
							encode_vars = lambda v: { 'req_data': brightcovedata(v['video_player'], 1199515803001, 656327052001, '2ba01fac60a902ffc3c6322c3ef5546dbcf393e4'),
														'headers': { 'Content-type': 'application/x-amf' },
														'req_url': 'http://c.brightcove.com/services/messagebroker/amf?playerKey=AQ~~,AAAAmNAkCuE~,RfA9vPhrJwdowytpDwHD00J5pjBMVHD6' } ),
						TemplateRequest(
							decode_content = decode_bc,
							re = r'"(?P<quality>\d+x\d+):(?P<final_url>[^&]+)&(?P<path>[^"]+)";',
							encode_vars = lambda v: { 'final_url': '%(final_url)s swfVfy=1 swfUrl=http://admin.brightcove.com/viewer/us1.25.04.01.2011-05-24182704/connection/ExternalConnection_2.swf playpath=%(path)s' % v,
													'suffix-hint': 'flv' } )] }]



post = {
   "version":3,
   "headers":[

   ],
   "bodies":[
      {
         "targetURI":"com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",
         "responseURI":"/1",
         "data":[
            "2ba01fac60a902ffc3c6322c3ef5546dbcf393e4",
            {
               "__className__":"com.brightcove.experience.ViewerExperienceRequest",
               "URL":"http://elitserienplay.se/video.2137283880001",
               "experienceId":0,
               "contentOverrides":[
                  {
                     "__className__":"com.brightcove.experience.ContentOverride",
                     "contentRefId":None,
                     "contentType":0,
                     "contentRefIds":None,
                     "target":"videoPlayer",
                     "featuredId":None,
                     "contentId":2137283880001,
                     "featuredRefId":None,
                     "contentIds":None
                  }
               ],
               "TTLToken":"",
               "deliveryType":None,
               "playerKey":"AQ~~,AAAAmNAkCuE~,RfA9vPhrJwdowytpDwHD00J5pjBMVHD6"
            }
         ]
      }
   ]
}


response = {
   "version":3,
   "headers":[

   ],
   "bodies":[
      {
         "targetURI":"/1/onResult",
         "responseURI":"",
         "data":{
            "__className__":"com.brightcove.templating.ViewerExperienceDTO",
            "analyticsTrackers":[
               "TR-89F-HNE",
               "TR-YZF-448"
            ],
            "publisherType":"PREMIUM",
            "publisherId":656327052001,
            "playerKey":"AQ~~,AAAAmNAkCuE~,RfA9vPhrJwdowytpDwHD00J5pjBMVHD6",
            "version":None,
            "programmedContent":{
               "videoPlayer":{
                  "__className__":"com.brightcove.player.programming.ProgrammedMediaDTO",
                  "id":None,
                  "mediaId":2137283880001,
                  "cause":-1,
                  "componentRefId":"videoPlayer",
                  "playerId":None,
                  "type":0,
                  "mediaDTO":{
                     "__className__":"com.brightcove.catalog.trimmed.VideoDTO",
                     "dateFiltered":False,
                     "FLVFullLengthStreamed":True,
                     "SWFVerificationRequired":False,
                     "endDate":None,
                     "FLVFullCodec":3,
                     "linkText":None,
                     "captions":None,
                     "previewLength":0,
                     "geoRestricted":False,
                     "FLVPreviewSize":0,
                     "longDescription":None,
                     "thumbnailURL":"http://brightcove01.brightcove.com/21/656327052001/201302/3576/656327052001_2137298353001_th-510d84fce4b02253b2b0c412-1592194043001.jpg?pubId=656327052001",
                     "FLVPreBumperURL":None,
                     "purchaseAmount":None,
                     "videoStillURL":"http://brightcove01.brightcove.com/21/656327052001/201302/2576/656327052001_2137298352001_vs-510d84fce4b02253b2b0c412-1592194043001.jpg?pubId=656327052001",
                     "sharedBy":None,
                     "yearProduced":None,
                     "cuePoints":None,
                     "submitted":False,
                     "customFieldValues":None,
                     "ratingEnum":None,
                     "IOSRenditions":[
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"http://c.brightcove.com/services/mobile/streaming/index/rendition.m3u8?assetId=2137298421001",
                           "encodingRate":608000,
                           "frameWidth":400,
                           "mediaDeliveryType":2,
                           "videoContainer":2,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":224,
                           "size":7848675
                        },
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"http://c.brightcove.com/services/mobile/streaming/index/rendition.m3u8?assetId=2137298614001",
                           "encodingRate":1196000,
                           "frameWidth":640,
                           "mediaDeliveryType":2,
                           "videoContainer":2,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":360,
                           "size":15577687
                        }
                     ],
                     "filterStartDate":None,
                     "shortDescription":"Medverkande: Janne Karlsson, Rgle; Sam Hallam, Vxj Lakers.",
                     "awards":None,
                     "rentalAmount":None,
                     "FLVFullSize":6222845,
                     "drmMetadataURL":None,
                     "economics":1,
                     "publishedDate":"2013-02-02T21:28:28.035Z",
                     "language":None,
                     "FLVFullLengthURL":"rtmp://cp101675.edgefcs.net/ondemand/&mp4:23/656327052001/201302/640/656327052001_2137298406001_SHL-VLH-20130202-221613-Press-vlh-rbk.mp4?__nn__=1545806548001&slist=23/656327052001/201302/1280/;23/656327052001/201302/2576/;23/656327052001/201302/2896/;23/656327052001/201302/640/&auth=daEb2bIbKdebTcmbXdJaydhaib4cFcKd_aB-brdLfa-bWG-CBBn_HBn_CEwH_ImF&aifp=rtmpeuds17",
                     "startDate":None,
                     "logoOverlay":None,
                     "forceAds":False,
                     "FLVPreviewURL":None,
                     "lineupId":None,
                     "version":None,
                     "id":2137283880001,
                     "isSubmitted":False,
                     "publisherName":"Sports Editing Sweden Ab",
                     "adKeys":None,
                     "length":102679,
                     "rentalPeriod":None,
                     "sharedByExternalAcct":False,
                     "adCategories":None,
                     "FLVPreviewStreamed":False,
                     "allowViralSyndication":True,
                     "FLVPreBumperStreamed":False,
                     "tags":[
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"Vxj Lakers HC",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"post_game",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"game_3835",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"club_RBK",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"season_1213",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"Rgle BK",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"club_VLH",
                           "image":None
                        },
                        {
                           "__className__":"com.brightcove.catalog.TagDTO",
                           "name":"Ssong 2012/2013",
                           "image":None
                        }
                     ],
                     "sharedSourceId":None,
                     "publisherId":656327052001,
                     "allowedCountries":[

                     ],
                     "controllerType":4,
                     "encodingRate":478267,
                     "monthlyAmount":None,
                     "customFields":{
                        "sitenetwork":"SHL",
                        "displayonesp":"True",
                        "ownerclub":"VLH",
                        "espvideotype":"intervju"
                     },
                     "filterEndDate":None,
                     "FLVPreviewCodec":0,
                     "referenceId":"esul_1359838779187390",
                     "WMVFullAssetId":None,
                     "numberOfPlays":0,
                     "sharedToExternalAcct":False,
                     "FLVPreBumperControllerType":0,
                     "creationDate":"2013-02-02T21:28:28.035Z",
                     "excludeListedCountries":False,
                     "color":None,
                     "renditions":[
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"rtmp://cp101675.edgefcs.net/ondemand/&mp4:23/656327052001/201302/2896/656327052001_2137298668001_SHL-VLH-20130202-221613-Press-vlh-rbk.mp4?__nn__=1545806548001&slist=23/656327052001/201302/1280/;23/656327052001/201302/2576/;23/656327052001/201302/2896/;23/656327052001/201302/640/&auth=daEb2bIbKdebTcmbXdJaydhaib4cFcKd_aB-brdLfa-bWG-CBBn_HBn_CEwH_ImF&aifp=rtmpeuds17",
                           "encodingRate":1764422,
                           "frameWidth":1280,
                           "mediaDeliveryType":0,
                           "videoContainer":1,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":720,
                           "size":22750123
                        },
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"rtmp://cp101675.edgefcs.net/ondemand/&mp4:23/656327052001/201302/640/656327052001_2137298406001_SHL-VLH-20130202-221613-Press-vlh-rbk.mp4?__nn__=1545806548001&slist=23/656327052001/201302/1280/;23/656327052001/201302/2576/;23/656327052001/201302/2896/;23/656327052001/201302/640/&auth=daEb2bIbKdebTcmbXdJaydhaib4cFcKd_aB-brdLfa-bWG-CBBn_HBn_CEwH_ImF&aifp=rtmpeuds17",
                           "encodingRate":478267,
                           "frameWidth":400,
                           "mediaDeliveryType":0,
                           "videoContainer":1,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":224,
                           "size":6222845
                        },
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"rtmp://cp101675.edgefcs.net/ondemand/&mp4:23/656327052001/201302/1280/656327052001_2137307262001_SHL-VLH-20130202-221613-Press-vlh-rbk.mp4?__nn__=1545806548001&slist=23/656327052001/201302/1280/;23/656327052001/201302/2576/;23/656327052001/201302/2896/;23/656327052001/201302/640/&auth=daEb2bIbKdebTcmbXdJaydhaib4cFcKd_aB-brdLfa-bWG-CBBn_HBn_CEwH_ImF&aifp=rtmpeuds17",
                           "encodingRate":4092422,
                           "frameWidth":1280,
                           "mediaDeliveryType":0,
                           "videoContainer":1,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":720,
                           "size":52468667
                        },
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"rtmp://cp101675.edgefcs.net/ondemand/&mp4:23/656327052001/201302/2576/656327052001_2137298348001_SHL-VLH-20130202-221613-Press-vlh-rbk.mp4?__nn__=1545806548001&slist=23/656327052001/201302/1280/;23/656327052001/201302/2576/;23/656327052001/201302/2896/;23/656327052001/201302/640/&auth=daEb2bIbKdebTcmbXdJaydhaib4cFcKd_aB-brdLfa-bWG-CBBn_HBn_CEwH_ImF&aifp=rtmpeuds17",
                           "encodingRate":818655,
                           "frameWidth":640,
                           "mediaDeliveryType":0,
                           "videoContainer":1,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":360,
                           "size":10565651
                        },
                        {
                           "__className__":"com.brightcove.catalog.trimmed.RenditionAssetDTO",
                           "defaultURL":"rtmp://cp101675.edgefcs.net/ondemand/&mp4:23/656327052001/201302/2896/656327052001_2137306876001_SHL-VLH-20130202-221613-Press-vlh-rbk.mp4?__nn__=1545806548001&slist=23/656327052001/201302/1280/;23/656327052001/201302/2576/;23/656327052001/201302/2896/;23/656327052001/201302/640/&auth=daEb2bIbKdebTcmbXdJaydhaib4cFcKd_aB-brdLfa-bWG-CBBn_HBn_CEwH_ImF&aifp=rtmpeuds17",
                           "encodingRate":1592422,
                           "frameWidth":1024,
                           "mediaDeliveryType":0,
                           "videoContainer":1,
                           "videoCodec":"H264",
                           "audioOnly":False,
                           "frameHeight":576,
                           "size":20505337
                        }
                     ],
                     "linkURL":None,
                     "categories":[

                     ],
                     "displayName":"Presskonferens VLH-RBK",
                     "WMVFullLengthURL":None
                  },
                  "version":None
               }
            },
            "adTranslationSWF":None,
            "id":1199515803001,
            "hasProgramming":False,
            "programmingComponents":[
               "videoPlayer"
            ],
            "adPolicy":{
               "__className__":"com.brightcove.ads.AdPolicyDTO",
               "playAdOnLoad":False,
               "timeAdPlayInterval":120,
               "timeBasedPolicy":False,
               "titleAdPlayInterval":1,
               "midrollAdKeys":None,
               "prerollAds":True,
               "postrollAds":False,
               "version":None,
               "id":None,
               "firstAdPlay":1,
               "midrollAds":False,
               "onLoadAdKeys":None,
               "postrollAdKeys":None,
               "adPlayCap":1,
               "titleBasedPolicy":True,
               "zone":0,
               "prerollAdKeys":None,
               "playerAdKeys":"vpDomain=http://se-hockeyligan.videoplaza.tv;vpBCMapShares=[ownerclub]/PLAY/[ownerclub];"
            },
            "adServerURL":"",
            "configuredProperties":{
               "application":{
                  "featureSwitches":"010111111",
                  "enableAPI":"True",
                  "html5Enabled":"True"
               },
               "videoPlayer":{
                  "removeBrightcoveMenu":"True",
                  "removeBranding":"True",
                  "allowViralTitle":"False",
                  "showNewest":"False",
                  "allowEmail":"False",
                  "showMostViewed":"False",
                  "showRelated":"False",
                  "allowLink":"False",
                  "endScreen":"stillScreen"
               }
            },
            "userCountry":None,
            "name":"Elitserien play COMMON",
            "linkBaseURL":"http://link.brightcove.com/services/player/bcpid1199515803001?bckey=AQ~~,AAAAmNAkCuE~,RfA9vPhrJwdowytpDwHD00J5pjBMVHD6",
            "layout":"\r\n<Runtime>\r\n  <Theme name=\"Deluxe\" style=\"Light\"/>\r\n  <Layout>\r\n    <ChromelessVideoPlayer id=\"videoPlayer\"/>\r\n  </Layout>\r\n</Runtime>",
            "linkURL":None,
            "isDefaultViralTemplate":False,
            "nextGenAnalyticsEnabled":True,
            "adPolicySWF":"http://se-hockeyligan.cdn.videoplaza.tv/resources/flash/brightcove/latest/vp_adrules.swf"
         }
      }
   ]
}