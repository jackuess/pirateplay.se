function finalEvent (e) {
	if (this.classList.toggle('selected')) {
		listItem = document.createElement("li");
		if (agentIsPlayer)
			listItem.innerHTML = "<a href=\"" + this.href + "\">Välj program</a>";
		else
			listItem.innerHTML = "<a href=\"" + this.href + "\">Gå till programmet</a> | <a href=\"http://pirateplay.se/generate;application.html?url=" + this.href + "\">Ladda ner med Pirateplay</a>";
		listItem.className = "selected";
		currMenu.contentList.insertBefore(listItem, this.nextSibling);
	}
	else
		currMenu.contentList.removeChild(this.nextSibling);
};

base2.DOM.bind(document);

var agentIsPlayer = navigator.userAgent.indexOf("Pirateplayer") != -1;

var currMenu;
var cache = [];
cache.push = function (obj) { //Safely assuming only one object
	obj.scrollTop = currMenu.contentList.scrollTop;
	currMenu.clear();
	document.querySelector('#back_button').classList.add('enabled');//document.getElementById('back_button').style.display = "block";
	Array.prototype.push.call(cache, obj);
}
cache.pop = function () {
	if (this.length < 2)
		document.querySelector('#back_button').classList.remove('enabled');//document.getElementById('back_button').style.display = "none";
	return Array.prototype.pop.call(cache);
}


base2.DOM.HTMLElement.prototype.containsText = function (str) {return getTextContent(this).toLowerCase().indexOf(str.toLowerCase()) > -1;};

document.addEventListener("DOMContentLoaded", function () {
	menuInitDOM();

	currMenu = new Menu("Välj kanal");
	currMenu.addItem("SVT", "http://www.svtplay.se/alfabetisk", function(e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//a[@class=\"playLetterLink\"]'", 'svt');
	});
	currMenu.addItem("TV3", "http://www.tv3play.se/program", function(e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//div[@id=\"main-content\"]//a[@href]'", 'tv3.programs');
	});
	currMenu.addItem("TV4", "http://www.tv4play.se/a_till_o_lista", function (e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//ul/li/h3/a'", 'tv4');
	});
	currMenu.addItem("Kanal 5", "http://www.kanal5play.se/program", function(e) {
		cache.push(currMenu.instance());
		//yqlReq("select * from html where url = '" + this.href + "' and xpath = '//a[@class=\"k5-AToZPanel-program k5-AToZPanel-channel-KANAL5\" or @class=\"k5-AToZPanel-program k5-AToZPanel-channel-KANAL5 k5-AToZPanel-program-topical\"]'", 'kanal5.programs');
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//a[@class=\"name ajax\"]'", 'kanal5.programs');
	});
	currMenu.addItem("TV6", "http://www.tv6play.se/program", function(e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//div[@id=\"main-content\"]//a[@href]'", 'tv6.programs');
	});
	currMenu.addItem("TV8", "http://www.tv8play.se/program", function(e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//div[@id=\"main-content\"]//a[@href]'", 'tv8.programs');
	});
	currMenu.addItem("Kanal 9", "http://www.kanal9play.se/program", function(e) {
		cache.push(currMenu.instance());
		yqlReq("select * from html where url = '" + this.href + "' and xpath = '//a[@class=\"k5-AToZPanel-program k5-AToZPanel-channel-KANAL9\" or @class=\"k5-AToZPanel-program k5-AToZPanel-channel-KANAL9 k5-AToZPanel-program-topical\"]'", 'kanal9.programs');
	});

	document.querySelector('#back_button').addEventListener("click", function (e) {
		//var contains = document.querySelector('#back_button').classList.contains || document.querySelector('#back_button').classList.has;
		var contains = document.querySelector('#back_button').classList.contains ? document.querySelector('#back_button').classList.contains('enabled') : document.querySelector('#back_button').classList.has('enabled');
		//if (!document.querySelector('#back_button').classList.contains('enabled'))
		if (!contains)
			return;
		currMenu.clear();
		document.getElementById('selector').innerHTML = "";
		currMenu = cache.pop();
		currMenu.render();
	}, false);

	currMenu.txtFilter.addEventListener('keyup', function (e) {
		currMenu.filter(this.value);
	}, false);
	currMenu.txtFilter.addEventListener('focus', function (e) {
		if (this.value == this.defaultValue)
			this.value = '';
	}, false);
	currMenu.txtFilter.addEventListener('blur', function (e) {
		if (this.value == '')
			this.value = this.defaultValue;
	}, false);

}, false);