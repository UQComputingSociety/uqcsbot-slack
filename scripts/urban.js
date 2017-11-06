// Description
//   Looks up a given phrase on Urban Dictionary
//
// Commands:
//   `!urban <PHRASE>` - Looks a phrase up on Urban Dictionary.
//

module.exports = function (robot) {
  robot.respond(/!?urban(.*)/i, function (res) {
    var phrase = res.match[1].trim();
    var urban = robot.http("http://api.urbandictionary.com/v0/define?term=" + encodeURI(phrase))
      .get()(function (err, resp, body) {

        // Check for correct usage
        if (res.match[1][0] !== " " || !phrase || phrase.length < 1) {
          return res.send("> Usage: `!urban <SEARCH_PHRASE>`");
        }

        // Check for JS/hubot errors
        if (err) {
          return res.send(">>> Error: " + err.toString() + ".");
        }

        // Check for HTTP Errors
        if (resp.statusCode !== 200) {
          return res.send("> HTTP Error ( " + resp.statusCode + ").");
        }

        var udResp = JSON.parse(body);

        // Parse Urban Dictionary response and send result.
        if (udResp["result_type"] !== undefined && udResp["result_type"] !== "no_results") {
          try {
            var firstResult = udResp["list"][0];
            var definition = firstResult["definition"];
            var example = firstResult["example"];
            var response = phrase.toUpperCase() + ":\n" + definition.toString() + "\n";
            if (example) {
              response += ">>> " + example.toString();
            }
            res.send(response);
            if (udResp["list"].length > 1) {
              res.send(" - more definitions at http://www.urbandictionary.com/define.php?term=" + encodeURI(phrase));
            }
            return;
          } catch(err) {
            return res.send(">>> Error parsing Urban Dictionary response: " + err.toString());
          }
        } else {
          return res.send("> No results found for " + phrase +". ¯\\_(ツ)_/¯")
        }
      });
  });
};
