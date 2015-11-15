// Description
//   Generates help commands for Hubot.
// 
// Commands:
//   !!acro <acronym> - Finds an acronym.
// 

var cheerio = require("cheerio");

module.exports = function (robot) {
  robot.hear(/^!!acro (.+)/i, function (res) {
    robot.getAcronyms(res, res.match[1].split(" "));
  });
  
  robot.getAcronyms = function (res, list) {
    var completed = 0;
    var responses = [];
    var limit = 5;

    var max = list.length;
    if (list.length > limit) {
      max = limit;
    }

    if (list.length == 1 && (list[0].toLowerCase() == ":horse:" || list[0] == "horse")) {
      res.send(">:taco:");
      return;
    }

    for (var i = 0; i < max; i++) {
      (function (index, title) {
        robot.http("http://acronyms.thefreedictionary.com/" + list[index]).get()(function (err, res, body) {
          if (!err) {
            responses[index] = body;
            completed++;
            if (completed == max) {
              var response = "";
              for (var j = 0; j < responses.length; j++) {
                var acro = title.toUpperCase();
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
      })(i, list[i]);
    }
  }
  
  robot.getAcronym = function (html) {
    var $ = cheerio.load(html);
    var responses = [];
    
    $('td.acr').each(function (i, element) {
      responses.push($(element).siblings().text());
    });
    
    return responses[Math.floor(Math.random() * responses.length)];
  }
}