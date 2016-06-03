// Description:
// Pulls a chunk of text from a relevent wikipedia entry.

// Dependencies:
// http
 
// Commands:
// !wiki <topic>

function queryWiki(msg, search) {
  var url;
  // check the api eh?
  url = "https://en.wikipedia.org/w/api.php?action=opensearch&search="
  		+search+"&format=json";
  return msg.http(url).get()(function(err, res, body) {
    var response = JSON.parse(body);
    var info = response[2][0];
    // if it gives suggestions just get the next best thing
    var typical = "may refer to:";
    if(info.indexOf(typical) >= 0) {
      // meh we tried
      return msg.send(response[2][1]);
    }
    // probably a good result
    return msg.send(info);
  });
};

module.exports = function(robot) {
  return robot.respond(/!?wiki(.*)/i, function(msg) {
    //extract the search term
    var query = msg.match[1].trim();
    search = query.replace(' ','%20');
    return queryWiki(msg, search);
  });
};
