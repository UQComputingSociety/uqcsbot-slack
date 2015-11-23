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

			// scrap the data
			$('table.chart').children().each(function (index, element) {
				var name  = $($(element).children()[0]).children().text().trim();
				var percent = $($($(element).children()[1]).children()).text().trim();
				var freeText = $($(element).children()[2]).text().trim();
				
				var free = freeText.split(' ')[0];
				var freeOf = freeText.split(' ')[3];
				
				/* res.send($(element).children());
				res.send('1 ' + name);
				res.send('2 ' + percent);
				res.send('3 ' + freeText);
				res.send('4 ' + free);
				res.send('5 ' + freeOf); */
				
				//console.log(name + ' is ' + percent + ' free. Of which ' + free + ' is free of ' + freeOf);
				computers.push([name, percent, free, freeOf]);	
			});

			var response = ">Available computers at St Lucia\r\n";
			
			for (var i = 0; i < computers.length; i++) {
				var name_r = computers[i][0];
				var percent_r = computers[i][1];
				var free_r = computers[i][2];
				var freeOf_r = computers[i][3];
				
				var realPercent = parseInt(Math.round(parseInt(percent_r.substring(0, percent_r.length-1)) / 10) * 10 / 2 / 10);
				
				response += ">_" + name_r + "_ *" + percent_r + "* " + (Array(5 - realPercent + 1).join(":no_entry:")) + (Array(realPercent + 1).join(":thumbsup:")) + " " + free_r + " computers free" + "\r\n";
			}
			
		res.send(response);
		});
	});
}
