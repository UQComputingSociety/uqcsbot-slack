// Description:
//   Gets the weather info or radar for st lucia by default or a specified location
//
//
// Commands:
//   !weather <location (opt)> - Gets the weather for a location (Defaults to Brisbane)
//   !weather radar <location (opt)> - Gets the closets BOM radar + weather
//

var kdt = require("kd.tree");

module.exports = function (robot) {
  robot.respond(/!?weather radar ?(.+)?/i, function (res) {
    var location = res.match[1] || "Brisbane";
    robot.getWeatherRadar(location, res)
  });

  robot.respond(/!?weather ?(.+)?/i, function (res) {
    var location = res.match[1] || "Brisbane";
    robot.getWeather(location, res)
  });

  robot.getWeatherRadar = function(location, res) {
    var query = 'https://maps.googleapis.com/maps/api/geocode/json?address='
      + encodeURIComponent(location)
      + '&region=au'
      + '&key=AIzaSyC1nwXyhwhcnV90evu0OeHkXC8yClJeaVI'; // Simon Victory's key
                                                        // Please dno not use

    var coords = [{ name: 'Bowen', url: 'http://www.bom.gov.au/products/IDR243.loop.shtml#skip', lat: '-19.88', long: '148.08' },
    { name: 'Brisbane (Mt. Stapylton)', url: 'http://www.bom.gov.au/products/IDR663.loop.shtml#skip', lat: '-27.718', long: '153.24' },
    { name: 'Cairns', url: 'http://www.bom.gov.au/products/IDR193.loop.shtml#skip', lat: '-16.82', long: '145.68' },
    { name: 'Emerald (Central Highlands)', url: 'http://www.bom.gov.au/products/IDR723.loop.shtml#skip', lat: '-23.5494', long: '148.2392' },
    { name: 'Gladstone', url: 'http://www.bom.gov.au/products/IDR233.loop.shtml#skip', lat: '-23.86', long: '151.26' },
    { name: 'Gympie (Mt Kanigan)', url: 'http://www.bom.gov.au/products/IDR083.loop.shtml#skip', lat: '-25.957', long: '152.577' },
    { name: 'Longreach', url: 'http://www.bom.gov.au/products/IDR563.loop.shtml#skip', lat: '-23.43', long: '144.29' },
    { name: 'Mackay', url: 'http://www.bom.gov.au/products/IDR223.loop.shtml#skip', lat: '-21.12', long: '149.22' },
    { name: 'Marburg', url: 'http://www.bom.gov.au/products/IDR503.loop.shtml#skip', lat: '-27.61', long: '152.54' },
    { name: 'Mount Isa', url: 'http://www.bom.gov.au/products/IDR363.loop.shtml#skip', lat: '-16.67', long: '139.17' },
    { name: 'Mornington Island', url: 'http://www.bom.gov.au/products/IDR753.loop.shtml#skip', lat: '-20.7114', long: '139.5553' },
    { name: 'Townsville (Hervey Range)', url: 'http://www.bom.gov.au/products/IDR733.loop.shtml#skip', lat: '-19.42', long: '146.55' },
    { name: 'Warrego', url: 'http://www.bom.gov.au/products/IDR673.loop.shtml#skip', lat: '-26.44', long: '147.35' },
    { name: 'Weipa', url: 'http://www.bom.gov.au/products/IDR783.loop.shtml#skip', lat: '-12.67', long: '141.92' },
    { name: 'Willis Island', url: 'http://www.bom.gov.au/products/IDR413.loop.shtml#skip', lat: '-16.288', long: '149.965' },
    { name: 'Canberra/Captains Flat', url: 'http://www.bom.gov.au/products/IDR403.loop.shtml#skip', lat: '-35.66', long: '149.51' },
    { name: 'Grafton', url: 'http://www.bom.gov.au/products/IDR283.loop.shtml#skip', lat: '-29.62', long: '152.97' },
    { name: 'Moree', url: 'http://www.bom.gov.au/products/IDR533.loop.shtml#skip', lat: '-29.50', long: '149.85' },
    { name: 'Namoi (Blackjack Mountain)', url: 'http://www.bom.gov.au/products/IDR693.loop.shtml#skip', lat: '-31.0240', long: '150.1915' },
    { name: 'Newcastle', url: 'http://www.bom.gov.au/products/IDR043.loop.shtml#skip', lat: '-32.730', long: '152.027' },
    { name: 'Norfolk Island', url: 'http://www.bom.gov.au/products/IDR623.loop.shtml#skip', lat: '-29.033', long: '167.933' },
    { name: 'Sydney (Terrey Hills)', url: 'http://www.bom.gov.au/products/IDR713.loop.shtml#skip', lat: '-33.701', long: '151.21' },
    { name: 'Wagga Wagga', url: 'http://www.bom.gov.au/products/IDR553.loop.shtml#skip', lat: '-35.17', long: '147.47' },
    { name: 'Wollongong (Appin)', url: 'http://www.bom.gov.au/products/IDR033.loop.shtml#skip', lat: '-34.264', long: '150.874' },
    { name: 'Alice Springs', url: 'http://www.bom.gov.au/products/IDR253.loop.shtml#skip', lat: '-23.82', long: '133.9' },
    { name: 'Darwin/Berrimah', url: 'http://www.bom.gov.au/products/IDR633.loop.shtml#skip', lat: '-12.46', long: '130.93' },
    { name: 'Gove', url: 'http://www.bom.gov.au/products/IDR093.loop.shtml#skip', lat: '-12.28', long: '136.82' },
    { name: 'Katherine/Tindal', url: 'http://www.bom.gov.au/products/IDR423.loop.shtml#skip', lat: '-14.51', long: '132.45' },
    { name: 'Adelaide (Buckland Park)', url: 'http://www.bom.gov.au/products/IDR643.loop.shtml#skip', lat: '-34.617', long: '138.469' },
    { name: 'Adelaide (Sellicks Hill)', url: 'http://www.bom.gov.au/products/IDR463.loop.shtml#skip', lat: '-35.33', long: '138.5' },
    { name: 'Ceduna', url: 'http://www.bom.gov.au/products/IDR333.loop.shtml#skip', lat: '-32.13', long: '133.7' },
    { name: 'Mt Gambier', url: 'http://www.bom.gov.au/products/IDR143.loop.shtml#skip', lat: '-37.75', long: '140.77' },
    { name: 'Woomera', url: 'http://www.bom.gov.au/products/IDR273.loop.shtml#skip', lat: '-31.16', long: '136.8' },
    { name: 'Hobart (Mt Koonya)', url: 'http://www.bom.gov.au/products/IDR763.loop.shtml#skip', lat: '-43.1122', long: '147.8061' },
    { name: 'West Takone', url: 'http://www.bom.gov.au/products/IDR523.loop.shtml#skip', lat: '-41.181', long: '145.579' },
    { name: 'Hobart Airport', url: 'http://www.bom.gov.au/products/IDR373.loop.shtml#skip', lat: '-42.83', long: '147.51' },
    { name: 'Melbourne', url: 'http://www.bom.gov.au/products/IDR023.loop.shtml#skip', lat: '-37.86', long: '144.76' },
    { name: 'Mildura', url: 'http://www.bom.gov.au/products/IDR303.loop.shtml#skip', lat: '-34.23', long: '142.08' },
    { name: 'Bairnsdale', url: 'http://www.bom.gov.au/products/IDR683.loop.shtml#skip', lat: '-37.89', long: '147.56' },
    { name: 'Yarrawonga', url: 'http://www.bom.gov.au/products/IDR493.loop.shtml#skip', lat: '-36.03', long: '146.03' },
    { name: 'Albany', url: 'http://www.bom.gov.au/products/IDR313.loop.shtml#skip', lat: '-34.94', long: '117.8' },
    { name: 'Broome', url: 'http://www.bom.gov.au/products/IDR173.loop.shtml#skip', lat: '-17.95', long: '122.23' },
    { name: 'Carnarvon', url: 'http://www.bom.gov.au/products/IDR053.loop.shtml#skip', lat: '-24.88', long: '113.67' },
    { name: 'Dampier', url: 'http://www.bom.gov.au/products/IDR153.loop.shtml#skip', lat: '-20.65', long: '116.69' },
    { name: 'Esperance', url: 'http://www.bom.gov.au/products/IDR323.loop.shtml#skip', lat: '-33.83', long: '121.89' },
    { name: 'Geraldton', url: 'http://www.bom.gov.au/products/IDR063.loop.shtml#skip', lat: '-28.80', long: '114.7' },
    { name: 'Giles', url: 'http://www.bom.gov.au/products/IDR443.loop.shtml#skip', lat: '-25.03', long: '128.3' },
    { name: 'Halls Creek', url: 'http://www.bom.gov.au/products/IDR393.loop.shtml#skip', lat: '-18.23', long: '127.66' },
    { name: 'Kalgoorlie-Boulder', url: 'http://www.bom.gov.au/products/IDR483.loop.shtml#skip', lat: '-30.79', long: '121.45' },
    { name: 'Learmonth', url: 'http://www.bom.gov.au/products/IDR293.loop.shtml#skip', lat: '-22.10', long: '114' },
    { name: 'Perth (Serpentine)', url: 'http://www.bom.gov.au/products/IDR703.loop.shtml#skip', lat: '-32.39', long: '115.87' },
    { name: 'Port Hedland', url: 'http://www.bom.gov.au/products/IDR163.loop.shtml#skip', lat: '-20.37', long: '118.63' },
    { name: 'Wyndham', url: 'http://www.bom.gov.au/products/IDR073.loop.shtml#skip', lat: '-15.45', long: '128.12' }];

    function distance(a, b) {
      var lat1 = a.lat,
      lon1 = a.long,
      lat2 = b.lat,
      lon2 = b.long;
      var rad = Math.PI/180;

      var dLat = (lat2-lat1)*rad;
      var dLon = (lon2-lon1)*rad;
      var lat1 = lat1*rad;
      var lat2 = lat2*rad;

      var x = Math.sin(dLat/2);
      var y = Math.sin(dLon/2);

      var a = x*x + y*y * Math.cos(lat1) * Math.cos(lat2);
      return Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }

    robot.http(query)
    .header('Accept', 'application/json')
    .get()
    (function(err, resp, body) {
      var json = JSON.parse(body);
      // robot.logger.info("Geocoded lat/long from search");
      // robot.logger.info(json.results[0].geometry.location.lat);
      // robot.logger.info(json.results[0].geometry.location.lng);
      lat = json.results[0].geometry.location.lat;
      lng = json.results[0].geometry.location.lng;

      var tree = kdt.createKdTree(coords, distance, ['lat', 'long']);
      var nearest = tree.nearest({ lat: lat, long: lng }, 1);

      // robot.logger.info("Nearest Australia radar");
      // robot.logger.info(nearest);
      res.send("Closest BOM radar :satellite: " + nearest[0][0].name + " :link: " + nearest[0][0].url);
    });
  };

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
