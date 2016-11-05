// Description
//   Finds pricing at umart for items
//
// Commands:
//   !`umart` _<parts...>_ - Finds an acronym.
//

var cheerio = require("cheerio");

module.exports = function (robot) {
	robot.respond(/!?umart (.+)/i, function (res) {
		robot.getPrices(res, res.match[1].trim().split(","));
	});

	robot.getPrices = function (res, list) {
		var completed = 0;
		var responses = [];
		var limit = 5;

		var max = list.length;
		if (list.length > limit) {
			max = limit;
		}

		if (list.length == 1) {
			if(list[0].toLowerCase() == "trm" || list[0] == "president") {
				res.send(">trm as president?\r\n>priceless");
				return;
			} else if(list[0].toLowerCase() == "cat" || list[0] == "treasurer") {
				res.send(">cat as treasurer?\r\n>$100000000000");
				return;
			} else if(list[0].toLowerCase() == "dmarj97" || list[0] == "secretary") {
				res.send(">dmarj97 as secretary?\r\n>200 slav squats");
				return;
			}
		}

		// Chain all the HTTP requests so its nice and synchronous
		for (var i = 0; i < max; i++) {
			// Keep everything in a closure so we can access the index variable later on
			(function (index) {
				robot.http("https://www.umart.com.au/umart1/pro/products_list_searchnew_min.phtml")
                    .header('Content-Type', 'application/x-www-form-urlencoded')
                    .post("search=" + list[index].trim() + "&bid=" + 2) // hardcode for Milton store
				(function (err, resp, body) {
					if (!err) {
						responses[index] = body;
						completed++;

						// Called when completing the final request
						if (completed == max) {
							var response = "```\r\n";
                            var results = [];
                            var maxPriceLength = 0;

							for (var j = 0; j < responses.length; j++) {
								var price = robot.getPrice(responses[j]);
								var title = robot.getTitle(responses[j]);

								if (price != false && title != false) {
									price = price || "$ ?";
									title = title || "No description found";
									results.push({price: price, title: title});

									if (price.length > maxPriceLength) {
										maxPriceLength = price.length;
									}									
								}
							}

                            for (var j = 0; j < results.length; j++) {
                                var item = results[j];
                                while (item.price.length < maxPriceLength) {
                                    item.price += " ";
                                }

                                response += item.price + " - " + item.title + "\r\n";
                            }

							if (results.length == 0) {
								response += "I can't find shit baus!\r\n";
							}

							if (list.length > limit) {
								response += "I am limited to " + limit + " items at once.";
							}

                            response += "```";

							res.send(response);
						}
					} else {
						return;
					}
				});
			})(i);
		}
	}

	robot.getTitle = function (html) {
		var $ = cheerio.load(html);
		var responses = [];

		$('a.proname').each(function (i, element) {
			responses.push($(element).text());
		});

		return responses.length > 0 ? responses[0] : false;
	}

	robot.getPrice = function (html) {
		var $ = cheerio.load(html);
		var responses = [];

		$('dl.dltwo > dd > span').each(function (i, element) {
			responses.push($(element).text());
		});

		return responses.length > 0 ? responses[0] : false;
	}
}
