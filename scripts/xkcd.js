//
// xkcd
//
// Commands:
//   !xkcd phrase 
//   Searches for an xkcd comic that is appropriate for that phrase
module.exports = function (robot) {
  robot.respond(/!?xkcd ?(.+)?/i, function (res) {
    // Get the query string
    var comic = res.match[1]
    if (!comic) {
      res.send("You actually need to search for something");
      return;
    }

    // Build the search URL
    var url = "https://relevantxkcd.appspot.com/process?action=xkcd&query=" + comic;
    robot.http(url).get()(function (err, resp, body) {
      // We get sent back a newline delimited list so split on that
      var r = body.split(/\n/);
      // We get sent back a the query execution time, a 0 (for success I assume?)
      // and n >= 1 result lines
      r = r[2].split(" ");
      // Each result line has the format `comiccode wikiurl`, and we want the code
      res.send("Search for `" + comic + "` gives: \n" + 
        "https://www.xkcd.com/" + r[0] + "/");
      return
    });
  });
};
