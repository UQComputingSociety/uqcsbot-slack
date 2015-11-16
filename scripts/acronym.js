// Description
//   Generates help commands for Hubot.
// 
// Commands:
//   !!acro <acronym> - Finds an acronym.
// 

var cheerio = require("cheerio");

module.exports = function (robot) {
  robot.hear(/^!!acro (.+)/i, function (res) {
    robot.getAcronyms(res, res.match[1].trim().split(" "));
  });
  
  robot.getAcronyms = function (res, list) {
    var completed = 0;
    var responses = [];
    var limit = 5;

    var max = list.length;
    if (list.length > limit) {
      max = limit;
    }

    // Requested by WBO, do not remove unless you get his express permission
    if(list.length == 1) {
      if(list[0].toLowerCase() == ":horse:" || list[0] == "horse") {
        res.send(">:taco:");
        return;
      } else if(list[0].toLowerCase() == ":rachel:" || list[0] == "rachel") {
        res.send(">:older_woman:");
        return;
      }
    }

    // Chain all the HTTP requests so its nice and synchronous
    for (var i = 0; i < max; i++) {
 
      // Keep everything in a closure so we can access the index variable later on
      (function (index) {
        robot.http("http://acronyms.thefreedictionary.com/" + list[index]).get()
        (function (err, resp, body) {
          if (!err) {
            responses[index] = body;
            completed++;
            
            // Called when completing the final request
            if (completed == max) {
              var response = "";
              for (var j = 0; j < responses.length; j++) {
                var acro = list[j].toUpperCase();
                var acronym = robot.getAcronym(responses[j]);
                response += ">" + acro + ": " + acronym + "\r\n";
              }
  
              if (list.length > 5) {
                response += ">I am limited to " + limit + " acronyms at once.";
              }
              res.send(response);
            }
          } else {
            return;
          }
        });
      })(i);
    }
  }
  
  // Parses the DOM to get the acroynm expansion
  robot.getAcronym = function (html) {
    var $ = cheerio.load(html);
    var responses = [];
    
    $('td.acr').each(function (i, element) {
      responses.push($(element).siblings().text());
    });
    
    return responses[Math.floor(Math.random() * responses.length)];
  }
}
