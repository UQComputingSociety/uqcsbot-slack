// Description
//   Gets the weather for st lucia by default or a specified location
// 
// Commands:
//   !weather <location (opt)> - Gets the weather for a location (Defaults to Brisbane) 
// 

var APPID = "6854f325de5158ff8020c1ea06333234";

module.exports = function (robot) {
  robot.hear(/^!weather ?(.+)?/i, function (res) {
	  var location = res.match[1] || "Brisbane";
	  robot.getWeather(location, res)
  });
  
  robot.getWeather = function(location, res) {
	  robot.http("http://api.openweathermap.org/data/2.5/weather?q=" + location + "&APPID=" + APPID).get()
	  (function(err, resp, body) {
		 var json = JSON.parse(body);
		 
		 if (json.cod.toString().trim() == "200") {
			 var temp = Math.round((json.main.temp - 273) * 100) / 100;
			 var humidity = json.main.humidity;
			 var min = Math.round((json.main.temp_min - 273) * 100) / 100;
			 var max = Math.round((json.main.temp_max - 273) * 100) / 100;
			 var weather = json.weather[0].description;
			 res.send(">*" + json.name + "* is *" + temp + "°C* (min: *" + min + "°C*, max: *" + max + "°C*) with humidity at *" + humidity + "%* and *" + weather + "*");
		 } else {
			 res.send(">Can't find " + location);
		 }
	  });
  }
}
