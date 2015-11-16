module.exports = function (robot) {
	robot.hear(/^!urban (.+)/i, function (res) {
		robot.getUrban(res, res.match[1].trim().split(" "));
	});

	robot.getUrban = function (res, list) {
		var completed = 0;
		var responses = [];
		var limit = 5;

		var max = list.length;
		if (list.length > limit) {
			max = limit;
		}

		// Chain all the HTTP requests so its nice and synchronous
		for (var i = 0; i < max; i++) {

			// Keep everything in a closure so we can access the index variable later on
			(function (index) {
				robot.http("http://api.urbandictionary.com/v0/define?term=" + list[index]).get()
				(function (err, resp, body) {
					if (!err) {
						responses[index] = body;
						completed++;

						// Called when completing the final request
						if (completed == max) {
							var response = "";
							for (var j = 0; j < responses.length; j++) {
								var word = list[j].toUpperCase();
								var definition = robot.getUrbanDef(responses[j]);
								var example = robot.getUrbanExample(responses[j]);
								response += ">" + word + ": " + definition + "\r\n";
								response += "> \t _" + example + "_ \r\n";
							}

							if (list.length > limit) {
								response += ">I am limited to " + limit + " searchs at once.";
							}
							res.send(response);
						}
					}
				});
			})(i);
		}
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