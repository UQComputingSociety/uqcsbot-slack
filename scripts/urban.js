// Description
//   Generates help commands for Hubot.
//
// Commands:
//   !urban <phrase> - Looks a phrase up on Urban Dictionary.
// 

module.exports = function (robot) {
	robot.hear(/^!urban (.+)/i, function (res) {
		robot.getUrban(res, res.match[1].trim());
	});

	robot.getUrban = function (res, word) {

		robot.http("http://api.urbandictionary.com/v0/define?term=" + word).get()
		(function (err, resp, body) {
			if (!err) {

				var response = "";
				var definition = robot.getUrbanDef(body);
				var example = robot.getUrbanExample(body);
				response += ">" + word + ": " + definition + "\r\n";
				response += "> \t _" + example + "_ \r\n";

				res.send(response);
			}
		});
	};

	// Parses the JSON to get the first definition
	robot.getUrbanDef = function (string) {
		json = JSON.parse(string);
		return json["list"][0]["definition"];
	};

	// Parses the JSON to get the first definition
	robot.getUrbanExample = function (string) {
		json = JSON.parse(string);
		return json["list"][0]["example"];
	};
};