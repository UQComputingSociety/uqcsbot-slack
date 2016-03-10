// Description
//   Generates help commands for Hubot.
// 
// Commands:
//   !parking - Lists the available parking at UQ
// 

var cheerio = require("cheerio");

module.exports = function (robot) {
	robot.respond(/!?parking/i, function (res) {
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
			
			var msgs = [];

			for (var i = 0; i < responses.length; i++) {
				var avail = responses[i][1];
				var parkName = responses[i][0];

				if (alias[parkName.toLowerCase()] != null) {
					parkName = alias[parkName.toLowerCase()];
				}

				var modifier = "has";
				var after = "";
				if (avail.toLowerCase().indexOf("full") > -1) {
					modifier = "is "; // NOTE THE SPACE
				} else {
					after = " parks";
				}

				msgs.push({
					msg: ">`" + parkName + " " + modifier + " ",
					avail: avail,
					after: after + "\r\n"
				});
				
				//response += ">`" + parkName + "` " + modifier + " *" + avail + "*" + after + "\r\n";
			}
			
			var max = 0;
			for (var i = 0; i < msgs.length; i++) {
				var item = msgs[i];
				var len = item.msg.length;
				if (len > max) {
					max = len;
				}
			}

			for (var i = 0; i < msgs.length; i++) {
				item = msgs[i];
				len = Math.max(item.msg.length, 0);
				len = Math.max(len, 0);
				
				response += item.msg;
				while (len < max) {
					response += " ";
					len++;
				}
				
				len = Math.max(item.avail.length, 0);
				while (len < "FULL".length) {
					response += " ";
					len++;
				}
				
				response += "` *" + item.avail + "*" + item.after;
			}
			
			res.send(response);
		});
	});
}