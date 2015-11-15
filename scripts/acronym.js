// Description
//   Generates help commands for Hubot.
// 
// Commands:
//   !!acro <acronym> - Finds an acronym.
// 

var cheerio = require("cheerio");

module.exports = function(robot){
  robot.hear(/^!!acro (.+)/i, function(res){
    var content = res.match[1];
    var acro = content.split(" ")[0].toUpperCase();
    robot.http("http://acronyms.thefreedictionary.com/"+acro).get()(function(err, resp, body){
      if(!err){
        var $ = cheerio.load(body);
        if($("table#AcrFinder").get().length != 1){
         res.send(acro+" not found.");
         return;
        }
        // this one-liner took wayyyy too long
        // $($('table#AcrFinder').first().children().get(1).children[1]).text()
        res.send (">"+acro+": "+$($('table#AcrFinder').first().children().get(1).children[1]).text());
        return;
      }
    });
  });
}