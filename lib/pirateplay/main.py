#!/usr/bin/python2

import getopt, sys, re, os.path
from os import system

from rerequest import *
from services import services

def rtmpdump_cmd(rtmp_url, out = '-'):
	cmd = (rtmp_url.replace('swfVfy=1 swfUrl=', '-W ')
					.replace('live=1', '-v')
					.replace('live=0', '')
					.replace('app=', '-a ')
					.replace('playpath=', '-y '))
	cmd = 'rtmpdump -r %s -o "%s"'% (cmd, out)
	return cmd

def get_streams(url):
	debug_print('Getting streams for: ' + url)
	for service in services:
		streams = service.get_streams(url)
		if len(streams) > 0:
			return streams, service.filename_hint
	return [], None

def quality2int(quality):
	''' Parse string like 720x580 or '820 kbps', return numeric quality. '''
	if re.match('[0-9]+x[0-9]+', quality):
		rows, columns = quality.split('x')
		return int(rows) * int(columns)
	match = re.match('^[0-9]+', quality)
	if match:
		return int(match.group())
	print "Don't understand quality: " + quality
	sys.exit(3)

def find_best_stream(cmds, max_quality, subs):
	''' Return 'best' stream, possibly constrained to matching subs. '''
	if subs:
		cmds = list([ c for c in cmds if c['subs'] == subs])
		if not cmds:
			print "No streams with %s subtitles" % subs
			sys.exit(2)
	best_stream = cmds[0]
	max_quality = quality2int(max_quality)
	best_quality = quality2int(best_stream['quality'])
	for cmd in cmds[1:]:
		cmd_pixels =  quality2int(cmd['quality'])
		if cmd_pixels > best_quality and cmd_pixels <= max_quality:
			best_stream = cmd
			best_quality = quality2int(cmd['quality'])
	return best_stream

def print_usage():
	print """Usage: pirateplay [Flags]... [URL]...
			Finds stream urls for swedish programming. Plays them in vlc by default. Downloads them if output file is specified.

			  -h, --help
			    Print this help text.
			  -p, --print
			    Print commands; don't execute them.
			  -P, --print-urls
			    Print urls, not commands.
			  -o file, --output-file=path
			    Download to file. If output-file is a directory, adds -f filename.
			  -y command, --player=command
			    Set player command, ie. ffplay, vlc, mplayer (default is vlc).
			  -f, --filename-hint
			    Print filename hint for download. Requires -o <directory>.
			  -a, --auto
			    Select stream (quality, subs) automagically.
			  -s, --subs
			    Preferred subs when --auto is used, ignored by default.
			  -r, --max-resolution
			    Max resolution when --auto is used e. g. '720x580' defaults to max available.
			  -d, --debug
			    Print debug info during execution.""".replace('	', '')
	sys.exit(0)

def parse_options():
	r = { 'play': True,
		'print_cmds': False,
		'print_urls': False,
		'player': 'vlc',
		'auto': False,
		'subs': None,
		'filename-hint': False,
		'out_file': '',
		'max-quality': '10000x10000' }
	opts, values = getopt.getopt(sys.argv[1:], 'pPy:dfo:as:r:h',
                                ['print', 'print-urls', 'player', 'debug',
								 'filename-hint', 'output-file=','auto', 'subs',
								 'max-resolution', 'help'])
	for o, v in opts:
		if o == '--print' or o == '-p':
			r['print_cmds'] = True
		elif o == '--print-urls' or o == '-P':
			r['print_urls'] = True
		elif o == '--player' or o == '-y':
			r['player'] = v
		elif o == '--debug' or o == '-d':
			set_debug(True)
		elif o == '--filename-hint' or o == '-f':
			r['filename-hint'] = True
		elif o == '--auto' or o == '-a':
			r['auto'] = True
		elif o == '--subs' or o == '-s':
			r['subs'] = v
		elif o == '--max-resolution' or o == '-r':
			r['max-quality'] = v
		elif o == '--output-file' or o == '-o':
			r['play'] = False
			if v == '':
				r['out_file'] = '-'
			else:
				r['out_file'] = v
		elif o == '--help' or o == '-h':
			print_usage()

		if r['filename-hint']:
			if not r['out_file'] or not os.path.isdir(r['out_file']):
				print "--filename-hint requires --output-file directory"
				sys.exit(1)
	return r

if __name__ == '__main__':
	options = parse_options()

	if system('which %s &> /dev/null' % options['player']) != 0:
		sys.exit('Player command not found: %s' % options['player'])
	streams, filename_hint = get_streams(sys.argv[-1])
	if not streams:
		print 'No streams found.'
		sys.exit(2)

	i = 0
	cmds = []
	for stream in streams:
		i += 1
		quality =  stream.metadict().get('quality', '0x0')
		pr_quality = quality if quality != '0x0' else  'unknown'
		subs = stream.metadict().get('subtitles', None)
		pr_subs = subs if subs else 'none'
		suffix_hint =  stream.metadict().get('suffix-hint', None)
		filename = options['out_file']
		if options['out_file'] and os.path.isdir(options['out_file']):
			filename = filename_hint
			if suffix_hint:
				filename += '.' + suffix_hint
			filename = os.path.join(options['out_file'], filename)
		if options['filename-hint']:
			print "Filename hint: " + filename
			sys.exit(0)

		print '%d. Quality: %s, subtitles: %s' % (i, pr_quality, pr_subs)

		if options['print_urls']:
			print stream.url
		else:
			if options['play']:
				cmd = "%s '%s'" % (options['player'], stream.url)
			elif stream.url.startswith('rtmp'):
				cmd = rtmpdump_cmd(stream.url, filename)
			elif '.m3u8' in stream.url:
				cmd = 'ffmpeg -i "%s" -acodec copy -vcodec copy -bsf aac_adtstoasc "%s"' % (stream.url, filename)
			elif 'manifest.f4m' in stream.url:
				cmd = 'php AdobeHDS.php --delete --manifest "%s" --outfile "%s"' % (stream.url, filename)
			else:
				cmd = 'wget -O "%s" "%s"' % (filename, stream.url)

			if options['print_cmds']:
				print cmd
			else:
				cmds.append({'cmd': cmd, 'quality': quality, 'subs': subs})

	if i == 1:
		print 'Running the single stream'
		system(cmds[0]['cmd'])
	elif not options['print_cmds'] and not options['print_urls']:
		if options['auto']:
			best_stream = find_best_stream(cmds, options['max-quality'], options['subs'])
			system(best_stream['cmd'])
		else:
			i_choice = int(raw_input('Choose stream: '))-1
			system(cmds[i_choice]['cmd'])


# vim: set noexpandtab ts=4 sw=4:

