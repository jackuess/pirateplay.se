function svt_episodes(r) {
	var episodes = r.query.results.a;
	
	if (episodes) {
		episodes = Array.isArray(episodes) ? episodes : [episodes];
		for (var i=0; i<episodes.length; i++)
			currMenu.addItem(episodes[i].header.h5, 'http://svtplay.se' + episodes[i].href, finalEvent);
	}
}

function svt(r) {
	var programs = r.query.results.a;
	var eventListener = function (e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" +  this.href + "' and xpath = '//div[@class=\"playBoxBody svtTab-1 svtTab-Active\"]//a[@class=\"playLink playFloatLeft playBox-Padded\" and header]' and compat='html5'", 'svt_episodes');
	};
	for (var i=0; i<programs.length; i++)
		currMenu.addItem(programs[i].content, 'http://www.svtplay.se' + programs[i].href + '?ajax,sb', eventListener);
	currMenu.setTitle("SVT Play");
}