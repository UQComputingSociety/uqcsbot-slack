//
// xkcd
//
// Commands:
//   `!xkcd <PHRASE>` - Searches for an xkcd comic that is appropriate for that phrase

module.exports = function (robot) {
  robot.respond(/!?xkcd ?(.+)?/i, function (res) {

    /**
     * Nicest SO answer I could find
     * http://stackoverflow.com/a/10835227
     */
    function isPositiveInteger(n) {
      return n >>> 0 === parseFloat(n);
    }

    /**
     * Search for xkcd comic by id
     */
    var idSearch = function (id) {
      var url = "https://www.xkcd.com/" + id + "/"
      robot.http(url).get()(function (err, resp, body) {
        if (resp.statusCode != 200) {
          res.send("Search on id `" + id + "` gives: \n That id isn't an id at all!");
          return;
        }
        res.send("Search on id `" + id + "` gives: \n" + url);
      });
    }

    /**
     * Search for xkcd comic on text
     */
    var textSearch = function (comic) {
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
    }

    // Get the query string
    var comic = res.match[1]
    if (!comic) {
      res.send("You actually need to search for something");
      return;
    } else if (isPositiveInteger(comic)) {
      idSearch(comic);
    } else {
      textSearch(comic);
    }
  });
};
