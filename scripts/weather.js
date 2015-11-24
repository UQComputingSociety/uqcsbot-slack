// Description
//   Gets the weather for st lucia by default or a specified location
// 
// Commands:
//   !weather <location (opt)> - Gets the weather for a location (Defaults to Brisbane) 
// 

module.exports = function (robot) {
	robot.hear(/^!weather ?(.+)?/i, function (res) {
		var location = res.match[1] || "Brisbane";
		robot.getWeather(location, res)
	});

	robot.getWeather = function(location, res) {
		var query = 'select * from weather.forecast where woeid in (select woeid from geo.places(1) where text="' + location + '") and u="c"';
		var url = "https://query.yahooapis.com/v1/public/yql?q=" + encodeURIComponent(query) + "&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys";

	robot.http(url).get()
		(function(err, resp, body) {
			var json = JSON.parse(body);
			var data = json.query.results.channel;
			var today = data.item.forecast[0];
			if (err == null) {
				var temp = Math.round(data.item.condition.temp * 100) / 100;
				var humidity = data.atmosphere.humidity;
				var min = Math.round(today.low * 100) / 100;
				var max = Math.round(today.high * 100) / 100;
				var weather = data.item.condition;
				res.send("> " + robot.getWeatherEmoji(parseInt(weather.code)) + " *" + data.location.city + ", " +
					data.location.country + "* is *" + temp + "°C* (min: *" + min+ "°C*, max: *" + max +
					"°C*) with humidity at *" + humidity + "%* and condition *" + weather.text + "*");
			} else {
				res.send(">Can't find " + location);
			}
		});
	}

	robot.getWeatherEmoji = function(code) {
		var result = "";

		if ([0, 2].indexOf(code) != -1) {
			result += ":tornado:";
		}
		if ([1, 3, 4, 37, 38, 39, 45, 47].indexOf(code) != -1) {
			result += ":thunder_cloud_and_rain:";
		}
		if ([5, 6, 7, 8, 10, 13, 14, 15, 16, 18, 25, 41, 42, 46].indexOf(code) != -1) {
			result += ":snowflake:";
		}
		if ([5, 10, 9, 11, 12, 35, 40].indexOf(code) != -1) {
			result += ":droplet:";
		}
		if ([17, 35].indexOf(code) != -1) {
			result += ":snow_cloud:";
		}
		if ([19, 20, 21, 22].indexOf(code) != -1) {
			result += ":fog:";
		}
		if ([23, 24].indexOf(code) != -1) {
			result += ":dash:";
		}
		if ([26, 27, 28].indexOf(code) != -1) {
			result += ":cloud:";
		}
		if ([29, 30, 44].indexOf(code) != -1) {
			result += ":partly_sunny:";
		}
		if ([31, 33].indexOf(code) != -1) {
			result += ":full_moon_with_face:";
		}
		if ([32, 34].indexOf(code) != -1) {
			result += ":sunny:";
		}

		return result;
	}
}
