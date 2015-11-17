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
			 var weather = data.item.condition.text;
			 res.send(">*" + data.location.city + ", " + data.location.country + "* is *" + temp + "°C* (min: *" + min + "°C*, max: *" + max + "°C*) with humidity at *" + humidity + "%* and condition *" + weather + "*");
		 } else {
			 res.send(">Can't find " + location);
		 }
	  });
  }
}
