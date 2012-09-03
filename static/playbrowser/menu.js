function menuItem(title, url, eventListener) {
	var listItem = document.createElement('li');
	
	if (eventListener === finalEvent && agentIsPlayer) {
		var anchor = document.createElement('a');
		setTextContent(anchor, title);
		anchor.href = url;
		listItem.appendChild(anchor);
	}
	else {
		listItem.addEventListener('click', eventListener, false);
		setTextContent(listItem, title);
		listItem.href = url;
	}

	return listItem;
}

function menuInitDOM () {
	Menu.prototype.contentList = document.getElementById('content');
	Menu.prototype.contentList.isLoading = false;
	Menu.prototype.header = document.getElementsByTagName('h2')[0];
	Menu.prototype.txtFilter = document.querySelector('#txtFilter');
}


function Menu(title) {
	this.setTitle(title);
	this.scrollTop = 0;
	this.strFilter = '';
	this.items = [];
}

Menu.prototype._addToDom = function (title, href, eventListener) {
	this.contentList.appendChild(menuItem(title, href, eventListener));
};
Menu.prototype.addItem = function (title, href, eventListener) {
	if (this.contentList.isLoading) {
		this.contentList.innerHTML = "";
		this.contentList.isLoading = false;
	}
	this.items.push({title: title, href: href, eventListener: eventListener});
	this._addToDom(title, href, eventListener);
};
Menu.prototype.setTitle = function (newTitle) {
	this.title = newTitle;
	setTextContent(this.header, newTitle);
}
Menu.prototype.render = function () {
	setTextContent(this.header, this.title);
	this.contentList.innerHTML = "";
	for (var i=0; i<this.items.length; i++) 
		this._addToDom(this.items[i].title, this.items[i].href, this.items[i].eventListener);
	if (this.strFilter != '') {
		this.txtFilter.value = this.strFilter;
		this.filter(this.strFilter);
	}
	this.contentList.scrollTop = this.scrollTop;
}
Menu.prototype.clear = function () {
	this.items = [];
	this.contentList.innerHTML = "<li>Laddar...</li>";
	this.contentList.isLoading = true;
	
	this.txtFilter.value = this.txtFilter.defaultValue;
}
Menu.prototype.instance = function () {
	var instans = new Menu(this.title);
	instans.items = this.items.slice();
	instans.scrollTop = this.scrollTop;
	instans.strFilter = this.txtFilter.value == this.txtFilter.defaultValue ? '' : this.txtFilter.value;
	return instans;
}
Menu.prototype.filter = function (str) {
	var child;
	for (var i=0; i<this.contentList.children.length; i++) {
		child = this.contentList.children[i];
		child.style.display = child.containsText(str) ? "block" : "none";
	}
}