function mtg (n) { this.number = n; }

mtg.prototype.episodes = function (r) {
	var episodes = r.query.results.tr;
	var seasonPrefix = "";

	for (var i=0; i<episodes.length; i++)
		if (episodes[i].td['class'] == "season-col")
			seasonPrefix = episodes[i].td.a.strong;
		else
			currMenu.addItem(seasonPrefix + ' avsnitt ' + episodes[i].td[0].p, 'http://tv' + this.number + 'play.se' + episodes[i].th.a.href, finalEvent);
}

mtg.prototype.programs = function (r) {
	var number = this.number;
	var programs = r.query.results.a;
	var eventListener = function (e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" +  this.href + "' and xpath = '//table[@class=\"clearfix clip-list video-tree\"]//tbody/tr'", 'tv' + number + '.episodes');
	};

	for (var i=0; i<programs.length; i++)
		currMenu.addItem(programs[i].content, 'http://tv' + number + 'play.se' + programs[i].href, eventListener);
	currMenu.setTitle("TV" + number + " Play");
}

var tv3 = new mtg('3');
var tv6 = new mtg('6');
var tv8 = new mtg('8');