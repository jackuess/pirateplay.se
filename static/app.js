function rtmpDumpCmd(url, out) {
	return 'rtmpdump  -o "' + out + '" -r ' +
			(url.replace(/playpath=/, '-y ')
				.replace(/swfVfy=1 swfUrl=/, '-W ')
				.replace(/app=/, '-a ')
				.replace(/live=1/, '-v '));
}

function stripExt(s) {
	return s.lastIndexOf('.') == -1 ? s : s.substr(0, s.lastIndexOf('.'));
}

function messages() {
	this.push = function (msg, type) {
		if (typeof type === 'undefined')
			var color = 'yellow';
		else if (type == 'success')
			var color = 'green';
		else if (type == 'error')
			var color = 'red';
		var r = $('<li class="box box-' + color + '">' + msg + '</li>');
		var close = $('<span class="close">Stäng</span>');
		close.click(function () { $(this).parent().remove(); });
		r.prepend(close);
		$('#messages').prepend(r);
	};
	this.flush = function () {
		$('#messages *').remove();
	};
}

function streamRepresentation(stream) {
	this.stream = stream;

	this.render = function (args) {
		var r = $('#result');
		r.show();
		$('#result_form').show();

		if ('quality' in this.stream.meta)
			r.append('<h2>Kvalitet: <em>' + this.stream.meta.quality + '</em></h2>')
		if ('subtitles' in this.stream.meta && this.stream.meta.subtitles != '')
			var subLink = '<a href="' + this.stream.meta.subtitles + '">' + this.stream.meta.subtitles + '</a>';
		
		if (args.show_inputs && (args.mode == 'download' || args.mode == 'play'))
			var streamLink = this.stream.url
		else
			var streamLink = '<a href="' + this.stream.url + '">' + this.stream.url + '</a>';
		
		if (args.mode == 'download') {
			if (this.stream.url.match(/^rtmpe?:\/\//) != null)
				cmd = rtmpDumpCmd(this.stream.url, args.out);
			else if (this.stream.url.match(/\.m3u8/) != null)
				cmd = 'ffmpeg -i "' + streamLink + '" -acodec copy -vcodec copy -bsf aac_adtstoasc "' + args.out + '"';
			else if (this.stream.url.match(/manifest\.f4m/) != null)
				cmd = 'php AdobeHDS.php --delete --manifest "' + streamLink + '" --outfile "' + args.out + '"';
			else
				cmd = 'wget -O "' + args.out + '" "' + streamLink + '"';
			
			if (args.show_inputs)
				r.append('<input type="text" class="cmd" value=\'' + cmd + "' />");
			else
				r.append('<p class="cmd">' + cmd + '</p>');
			if (subLink) {
				subCmd = 'wget -O "' + stripExt(args.out) + '.srt" "' + subLink + '"'
				if (args.show_inputs)
					r.append('<input type="text" class="cmd" value=\'' + subCmd + "' />");
				else
					r.append('<p class="cmd">' + subCmd + '</p>');
			}
		}
		else if (args.mode == 'show') {
			r.append('<p>Videoström: ' + streamLink + '</p>');
			if (subLink)
			r.append('<p>Undertexter: ' + subLink + '</p>');
		}
		else if (args.mode == 'play') {
			if (args.show_inputs)
				r.append('<input type="text" class="cmd" value=\'' + args.player + ' "' + this.stream.url + '"\' />');
			else
				r.append('<p class="cmd">' + args.player + ' "' + streamLink + '"</p>');
		}
	}
}

function streamCollection(streams) {
	this.currStreams = [];
	var _this = this;
	$(streams).each(function (i, s) {
		_this.currStreams.push(new streamRepresentation(s));;
	});

	this.render = function (args) {
		$('#result :not(.close)').remove();
		$(this.currStreams).each(function (i, s) {
			s.render(args);
		});
	}
}

function getForm() {
	var args = {};
	args.out = $('#out').val();
	args.mode = $('input[name="action"]:checked').val();
	args.show_inputs = $('input[name="show_inputs"]:checked').length > 0;
	if (args.mode == 'play')
		args.player = $('#player').val();
	return args;
}

function onStreams(streams) {
	myStreamCollection = new streamCollection(streams);
	var countingWords = ['Noll', 'En', 'Två', 'Tre', 'Fyra', 'Fem', 'Sex', 'Sju', 'Åtta', 'Nio', 'Tio', 'Elva', 'Tolv', 'Tretton'];

	myMessages.flush();
	myMessages.push((streams.length < 14 ? countingWords[streams.length] : streams.length) + ' ' + (streams.length == 1 ? 'ström funnen!' : 'strömmar funna!'), 'success');
	myStreamCollection.render(getForm());
}

function requestStreams(e) {
	var url = $('#url').val();

	if (pattern.test(url)) {
		$.get('api/get_streams.js', { url: url, rnd: + $.now() }, onStreams);
		myMessages.push('Laddar...');
		document.location = '#' + url;
	}
	else
		myMessages.push('Ogiltig address!', 'error');

	e.preventDefault();
}

function setPattern(services) {
	p = '';
	$(services).each(function (i, s) {
		if ('test' in s)
			p += '(' + s.test + ')|';
	});
	pattern = new RegExp(p.slice(0, -1));
}

var myStreamCollection = {render: function () {;}};
var myMessages = new messages();
var pattern = new RegExp('^.*');

$(document).ready(function () {
	var adressForm = $('form:first');
	$.get('api/services.js', { rnd: $.now() }, setPattern);
	adressForm.submit(requestStreams);
	$('#out').keyup(function () { myStreamCollection.render(getForm()); });
	$('#player').click(function () { myStreamCollection.render(getForm()); });
	$('#show_inputs').click(function () { myStreamCollection.render(getForm()); });
	$('#result .close').click(function () { $('#result').hide(); $('#result_form').hide(); });
	$('.download').hide(); //Avoiding countering CSS rules
	$('input[name="action"]').click(function () {
		if ($(this).val() == 'show')
			{ $('.out').hide(); $('.player').hide(); $('.download').hide(); }
		else if ($(this).val() == 'download')
			{ $('.out').show(); $('.player').hide(); $('.download').show(); }
		else if ($(this).val() == 'play')
			{ $('.out').hide(); $('.player').show(); $('.download').show(); }
		myStreamCollection.render(getForm());
	});
	$('#url').focus();
	
	var hashUrl = document.location.hash.substr(1);
	if(hashUrl != '') {
		$('#url').val(hashUrl);
		adressForm.trigger('submit');
	}
});