function isoDecode(s) { return s.replace(/%E5/g, 'å').replace(/%E4/g, 'ä').replace(/%F6/g, 'ö'); }

function kanal59(n) { this.number = n; };

kanal59.prototype.episodes = function (r) {
	var results = r.query.results;
	var contentList = document.getElementById('content');
	var number = this.number;

	if(typeof results.body.div[0].div.div.div.div[3].div[0].div[0].table !== "undefined" && typeof results.body.div[0].div.div.div.div[3].div[0].div[0].table.tr.td[1] !== "undefined") {
		var seasons = results.body.div[0].div.div.div.div[3].div[0].div[0].table.tr.td[1].div.div;
		var eventListener = function (e) {
			currMenu.clear();
			yqlReq("select * from html where url = '" +  decodeURIComponent(this.href).replace(/\+/g, '%20') + "' and xpath = '//a[@title]'", 'kanal' + number + '.episodes2');
		};
		var selectorList = document.getElementById('selector');
		for (var i=0; i<seasons.length; i++)
			selectorList.appendChild(menuItem('Säsong ' + seasons[i].p.content, 'http://www.kanal' + number + 'play.se' + seasons[i].p.span.content, eventListener));
	}

	var episodesRows = results.body.div[0].div.div.div.div[3].div[1].div.div[0].div.table.tr;
	episodesRows = Array.isArray(episodesRows) ? episodesRows : [episodesRows];
	for (var y = 0; y<episodesRows.length; y++)
		for (var x = 0; x<episodesRows[y].td.length; x++)
			currMenu.addItem(episodesRows[y].td[x].div.div.div[0].a.title, 'http://kanal' + number + 'play.se' + isoDecode(episodesRows[y].td[x].div.div.div[0].a.href), finalEvent);
};

kanal59.prototype.episodes2 = function (r) {
	var episodes = r.query.results.a;
	for (var i=0; i<episodes.length; i++)
		currMenu.addItem(episodes[i].title, 'http://kanal' + this.number + 'play.se' + isoDecode(episodes[i].href), finalEvent);
}

kanal59.prototype.programs = function (r) {
	var programs = r.query.results.a;
	var number = this.number;
	var eventListener = function (e) {
				cache.push(currMenu.instance());
	 			yqlReq("select * from html where url = '" +  this.href + "'", 'kanal' + number + '.episodes');
			};
	for (var i=0; i<programs.length; i++)
		currMenu.addItem(programs[i].content, 'http://kanal' + this.number + 'play.se' + isoDecode(programs[i].href), eventListener);
	currMenu.setTitle("Kanal " + number + " play");
}

//var kanal5 = new kanal59('5');
var kanal9 = new kanal59('9');

function kanal5() { ; }

kanal5.episodes = function (r) {
	var episodes = r.query.results.a;
	episodes = Array.isArray(episodes) ? episodes : [episodes];
	for (var i=0; i<episodes.length; i++)
		currMenu.addItem(episodes[i].content, 'http://kanal5play.se' + episodes[i].href, finalEvent);
}

kanal5.seasons = function (r) {
	var seasons = r.query.results.h2;
	var programUrl = r.query.diagnostics.url.content;
	var eventListener = function (e) {
		cache.push(currMenu.instance());
	 	yqlReq("select * from html where url = '" +  this.href + "' and xpath = '//td/h4/a'", 'kanal5.episodes');
	};
	seasons = Array.isArray(seasons) ? seasons : [seasons];
	for (var i=0; i<seasons.length; i++)
		currMenu.addItem(seasons[i].content, programUrl + '/sasong/' + (seasons.length-i), eventListener);
}

kanal5.programs = function (r) {
	var programs = r.query.results.a;
	var eventListener = function (e) {
		cache.push(currMenu.instance());
	 	yqlReq("select * from html where url = '" +  this.href + "' and xpath = '//h2[@class=\"season-header\"]'", 'kanal5.seasons');
	};
	for (var i=0; i<programs.length; i++)
		currMenu.addItem(programs[i].content, 'http://kanal5play.se' + programs[i].href, eventListener);
	currMenu.setTitle("Kanal 5 play");
}