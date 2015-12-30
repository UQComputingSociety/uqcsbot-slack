// Description
//   Returns the availability list of library computers at St Lucia
//
// Commands:
//   !computers - Lists the available computers at UQ
//

var cheerio = require("cheerio");

module.exports = function (robot) {
	robot.hear(/^!computers/i, function (res) {
		robot.http("https://www.library.uq.edu.au/uqlsm/availablepcsembed.php?stlucia").get() (function(err, resp, body) {
			var $ = cheerio.load(body);
			var computers = [];

			var emoji = [':building_construction:', ':biohazard_sign:', ':wrench:',
									 ':office:', ':graph:', ':sparkling_heart:', ':scales:',
									 ':speech_balloon:'];
									 //there's no real emoji support for ☤

			// scrap the data
			$('table.chart').children().each(function (index, element) {
				var name  = $($(element).children()[0]).children().text().trim();
				var percent = $($($(element).children()[1]).children()).text().trim();
				var freeText = $($(element).children()[2]).text().trim();

				var free = freeText.split(' ')[0];
				var freeOf = freeText.split(' ')[3];

				computers.push([name, percent, free, freeOf, emoji[index]]);
			});

			var response = ">Available computers :computer: at St Lucia\r\n";

			for (var i = 0; i < computers.length; i++) {
				var name_r = computers[i][0];
				var percent_r = computers[i][1];
				var free_r = computers[i][2];
				var freeOf_r = computers[i][3];

				var takenPercentage = Math.round(parseInt(percent_r.substring(0, percent_r.length-1)));
				var asciiPercentage = Math.round(takenPercentage / 2 / 10);

				var precentSpace = (parseInt(percent_r.substring(0, percent_r.length-1)) <= 9 ? 2 : 1);
				var freeSpace = "  ";
				if (free_r.toString().length == 1) {
					freeSpace = "   ";
				} else if (free_r.toString().length == 3) {
					freeSpace = " ";
				} else {}

				response += ">" + (Array(5 - asciiPercentage + 1).join("█"))
				 + (Array(asciiPercentage + 1).join("▒")) + " *"
				 + (100 - takenPercentage) + "% taken" + "*"
				 + (Array(precentSpace).join(" ")) + " - _" + free_r + "_" + freeSpace
				 + "computers free @ " + computers[i][4] + " _" + name_r + "_" + "\r\n";
			}

			res.send(response);
		});
	});
}
