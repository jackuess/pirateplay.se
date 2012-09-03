function yqlReq (yql, callback) {
	var head = document.getElementsByTagName("head")[0];
	script = document.createElement('script');
	script.type = 'text/javascript';
	script.src = "http://query.yahooapis.com/v1/public/yql?q=" + encodeURIComponent(yql) + '&format=json&diagnostics=true&callback=' + callback;
	head.appendChild(script);
}

function getTextContent (element) {
	return 'textContent' in element ? element.textContent : element.innerText;
}

function setTextContent (element, newText) {
	if ('textContent' in element)
		element.textContent = newText;
	else if ('innerText' in element)
		element.innerText = newText;
}