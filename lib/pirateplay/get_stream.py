#!/usr/bin/python2

import getopt, sys
from os import system

from rerequest2 import get_vars, debug_print, set_debug
from services2 import services

def rtmpdump_cmd(rtmp_url, out = '-'):
	cmd = (rtmp_url.replace('swfVfy=1 swfUrl=', '-W ')
					.replace('live=1', '-v')
					.replace('live=0', '')
					.replace('app=', '-a ')
					.replace('playpath=', '-y '))
	cmd = 'rtmpdump -r %s -o "%s"'% (cmd, out)
	return cmd

def sorted_streams(streams):
	return sorted(streams,
					key=lambda s: s.get('quality', '').rjust(16, '0'),
					reverse=True)
	
def remove_duplicates(streams):
	return dict([(s['final_url'], s) for s in streams]).values()

def get_streams(url):
	cache = {}
	debug_print('Getting streams for: ' + url)
	for service in services:
		streams = get_vars(service, url, cache)
		if len(streams) > 0:
			streams = remove_duplicates(streams)
			streams = sorted_streams(streams)
			return streams
	return []

def print_usage():
	print("""Usage: pirateplay [Flags]... [URL]...
			Finds stream urls for swedish programming. Plays them in vlc by default. Downloads them if output file is specified.

			  -h, --help
			    Print this help text.
			  -p, --print
			    Print commands; don't execute them.
			  -P, --print-urls
			    Print urls, not commands.
			  -o file, --output-file=file
			    Download to file.
			  -y command, --player=command
			    Set player command, ie. ffplay, vlc, mplayer (default is vlc).
			  -d, --debug
			    Print debug info during execution.""".replace('	', ''))
	sys.exit(0)

def parse_options():
	r = { 'play': True,
		'print_cmds': False,
		'print_urls': False,
		'player': 'vlc' }
	opts, values = getopt.getopt(sys.argv[1:], 'pPy:do:h', ['print', 'print-urls', 'player', 'debug', 'output-file=', 'help'])
	for o, v in opts:
		if o == '--print' or o == '-p':
			r['print_cmds'] = True
		elif o == '--print-urls' or o == '-P':
			r['print_urls'] = True
		elif o == '--player' or o == '-y':
			r['player'] = v
		elif o == '--debug' or o == '-d':
			set_debug(True)
		elif o == '--output-file' or o == '-o':
			r['play'] = False
			if v == '':
				r['out_file'] = '-'
			else:
				r['out_file'] = v
		elif o == '--help' or o == '-h':
			print_usage()
	
	return r

if __name__ == '__main__':
	options = parse_options()

	if system('which %s &> /dev/null' % options['player']) != 0:
		sys.exit('Player command not found: %s' % options['player'])

	streams = get_streams(sys.argv[-1])
	
	i = 0
	cmds = []
	for stream in streams:
		print('%d. Quality: %s, subtitles: %s' % (i+1, stream.get('quality', 'unknown'), stream.get('subtitles', 'none')))
		i += 1
		
		if options['print_urls']:
			print(stream['final_url'])
		else:
			if options['play']:
				cmd = "%s '%s'" % (options['player'], stream['final_url'])
			elif ['final_url'].startswith('rtmp'):
				cmd = rtmpdump_cmd(['final_url'], options['out_file'])
			elif '.m3u8' in ['final_url']:
				cmd = 'ffmpeg -i "%s" -acodec copy -vcodec copy -bsf aac_adtstoasc "%s"' % (stream['final_url'], options['out_file'])
			elif 'manifest.f4m' in ['final_url']:
				cmd = 'php AdobeHDS.php --delete --manifest "%s" --outfile "%s"' % (stream['final_url'], options['out_file'])
			else:
				cmd = 'wget -O "%s" "%s"' % (options['out_file'], ['final_url'])
			
			if options['print_cmds']:
				print(cmd)
			else:
				cmds.append(cmd)
	
	if i == 0:
		print('No streams found.')
	elif not options['print_cmds'] and not options['print_urls']:
		i_choice = int(raw_input('Choose stream: '))-1
		system(cmds[i_choice])
