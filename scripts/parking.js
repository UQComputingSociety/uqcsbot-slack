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
        "p11": "Conifer",
        "p10": "UQ Centre",
        "p8": "Boatshed 2 Storey",
        "p9": "Boatshed Open",
        "p7": "Dustbowl" 
      };
      
      var response = ">Parking at the University of Queensland";
      
      var formatted = [];
      for (var i = 0; i < responses.length; i++) {
        if (parks == 0) {
          response += ">";
        }
        
        var avail = responses[i][1];
        var parkName = responses[i][0];
        if (alias[parkName.toLowerCase()] != null) {
          parkName = alias[parkName.toLowerCase()];
        }
        
        formatted.push("_" + parkName + "_ has *" + avail + "* ");
      }
      
      var max = 0;
      for (var i = 0; i < formatted.length; i++) {
        if (max < formatted[i].length) {
          max = formatted[i].length;
        }
      }
      
      var parksPerRow = 4;
      var parks = 0;
      for (var i = 0; i < formatted.length; i++) {
        if (parks == 0) {
          response += ">";
        }
        
        response += formatted[i];
        
        for (var j = 0; j < max - formatted[i].length; j++) {
          response += " ";
        }
        
        if (parks < parksPerRow) {
          parks++;          
        } else {
          response += "\r\n";
          parks = 0;
        }
      }
      
      res.send(response);
    });
  });
}