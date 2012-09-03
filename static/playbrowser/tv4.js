function tv4_episodes (r) {
	if (r.query.results) {
		var episodes = r.query.results.a;
		episodes = Array.isArray(episodes) ? episodes : [episodes];
		for (var i=0; i<episodes.length; i++)
			currMenu.addItem(episodes[i].content, episodes[i].href, finalEvent);
	}
	else
		currMenu.addItem("Inga episoder", "#", null);
}

function tv42 (r) {
	yqlReq("select * from html where url = 'http://tv4play.se/search?order=desc&amp;rows=1000&amp;sorttype=date&amp;video_types=programs&amp;categoryids=" + r.query.results.input.value + "' and xpath = '//li[starts-with(@class, \"video-panel clip\") and not(.//p[@class=\"premium\"])]//h3[@class=\"video-title\"]/a'", 'tv4_episodes');
}

function tv4 (r) {
	var programs = r.query.results.a;
	var eventListener = function (e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" +  this.href + "' and xpath = '(//form[@class=\"search-state-form\" and not(./input[@value=\"clips\"])])[1]/input[@name=\"categoryids\"]'", 'tv42');
	};
	for (var i=0; i<programs.length; i++)
		currMenu.addItem(programs[i].content, 'http://tv4play.se' + programs[i].href, eventListener);
	currMenu.setTitle("TV4 Play");
}