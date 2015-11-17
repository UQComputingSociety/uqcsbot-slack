// Description
//   Generates help commands for Hubot.
// 
// Commands:
//   !parking - Lists the available parking at UQ
// 

var cheerio = require("cheerio");

module.exports = function (robot) {
	robot.hear(/^!parking/i, function (res) {
		robot.http("https://pg.pf.uq.edu.au/").get() (function(err, resp, body) {
			var $ = cheerio.load(body);
			var responses = [];

			$('table#parkingAvailability').children().each(function (index, element) {
				if ($(element).find("th").length > 0) {
					// Do nothing, its the header
				} else {
					var park = $($(element).children()[0]).text().trim();
					var permit = $($(element).children()[1]).text().trim();
					var casual = $($(element).children()[2]).text().trim();
					
					if (permit.length != 0) {
						responses.push([park, permit]);
					} else {
						responses.push([park, casual]);
					}	
				}
			});

			var alias = {
				"p12": "Daycare",
				"p11 l1": "Conifer L1 (Staff)",
				"p11 l2": "Conifer L2 (Staff)",
				"p11 l3": "Conifer L3 (Students)",
				"p10": "UQ Centre",
				"p9": "Boatshed Open",
				"p8 l1": "Boatshed Bottom",
				"p8 l2": "Boatshed Top",
				"p7": "Dustbowl",
				"p6": "BSL Short Term",
				"p5": "P5",
				"p4": "Multi Level 3",
				"p3": "Multi Level 2",
				"p2": "Multi Level 1",
				"p1": "Warehouse"
			};

			var response = ">Available parking at the University of Queensland\r\n";

			for (var i = 0; i < responses.length; i++) {
				var avail = responses[i][1];
				var parkName = responses[i][0];

				if (alias[parkName.toLowerCase()] != null) {
					parkName = alias[parkName.toLowerCase()];
				}

				var modifier = "has";
				var after = "";
				if (avail.toLowerCase().indexOf("full") > -1) {
					modifier = "is";
				} else {
					after = " parks";
				}

				response += ">_" + parkName + "_ " + modifier + " *" + avail + "*" + after + "\r\n";
			}

			res.send(response);
		});
	});
}