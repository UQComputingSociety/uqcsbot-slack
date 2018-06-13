// Description
//   Looks up a given phrase on Urban Dictionary
//
// Commands:
//   `!urban <PHRASE>` - Looks a phrase up on Urban Dictionary.
//

module.exports = function (robot) {
  robot.respond(/!?urban( .+)?/i, function (res) {

    // Check for correct usage
    if (!res.match[1] || res.match[1].length < 1) {
      return res.send("> Usage: `!urban <SEARCH_PHRASE>`");
    }

    var phrase = res.match[1].trim();

    var urban = robot.http("http://api.urbandictionary.com/v0/define?term=" + encodeURI(phrase))
      .get()(function (err, resp, body) {

        // Check that a response was received.
        if (err) {
          return res.send(">>> Error: " + err.toString() + ".");
        }

        // Check for HTTP Errors.
        if (resp.statusCode !== 200) {
          return res.send("> HTTP Error ( " + resp.statusCode + ").");
        }

        var udResp = JSON.parse(body); // The urban dictionary response, parsed into a JSON object.

        // Check that a result was found.
        if (udResp["result_type"] !== 'exact') {
          return res.send("> No results found for " + phrase +". ¯\\_(ツ)_/¯")
        }

        // Parse Urban Dictionary response and send result.
        var room = res.envelope.room; // Room the command was sent in.
        var firstResult = udResp["list"][0];
        var definition = firstResult["definition"];
        var example = firstResult["example"];
        var response = "*" + phrase.toLowerCase().replace(/\b\w/g, l => l.toUpperCase()) + ":* \n" + definition + "\n";
        if (example) {
          response += ">>> " + example;
        }
        var more = "";
        if (udResp["list"].length > 1) {
          more += "_ more definitions at www.urbandictionary.com/define.php?term=" + encodeURI(phrase) + " _";
        }
        robot.send({room: room}, response)[0].then(res => robot.send({room: room}, more));
      });
  });
};
