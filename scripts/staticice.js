// Description
//		A script to find the best prices for electronics in Aus based on the staticice search
//
// Commands:
//		!staticice <item name> -n <number of items>
//		if -n isn't specified the number of items listed is 5
//


var cheerio = require("cheerio");

module.exports = function (robot) {

	function printItems(res, item) {
	 	if (item.match(/-n/g) != null) {
			var links = item.match(/-n\s([0-9]{0,3})/g)[0].match(/[0-9]+/)[0];
		} else {
			var links = 5;
		}
	 	item = item.replace(/-n\s([0-9]{0,3})/g, "").trim().replace(/\s/g, "+");;
	 	var URL = "http://www.staticice.com.au/cgi-bin/search.cgi?q=" + item + "&links=" + links;
	 	robot.http(URL).get() (function(err, resp, body) {
	 		$ = cheerio.load(body);
	 		$('tr[valign="top"]').each(function(i, elem) {
	 			if (links > 0) {res.send($(this).text());}
	 			links--
	 		});
	 	});
	}

	// Response if no args given
	robot.respond(/!?staticice$/, function	(res) {
		res.send(["Staticice requires a item to search for and optionally a -n <number of items>"])
	});

	// Response if args given
	robot.respond(/!?staticice (.*)$/, function (res) {
		printItems(res, res.match[1]);
	});
};
