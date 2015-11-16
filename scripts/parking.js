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
        "p12": "Daycare",
        "p11 l1": "Conifer L1 (Staff)",
        "p11 l2": "Conifer L2 (Staff)",
        "p11 l3": "Conifer L3 (Students)",
        "p10": "UQ Centre",
        "p9": "Boatshed Open",
        "p8 l1": "Boatshed Bot",
        "p8 l2": "Boatshed Top",
        "p7": "Dustbowl",
        "p6": "BSL Short Term",
        "p5": "P5",
        "p4": "Multi Level",
        "p3": "Multi Level",
        "p2": "P2",
        "p1": "P1"
      };
      
      var response = ">Available parking at the University of Queensland\r\n";
      
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
        
        if (parks + 1 < parksPerRow) {
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