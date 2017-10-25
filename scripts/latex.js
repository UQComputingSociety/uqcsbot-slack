// Description
//   Converts text wrapped in LaTeX characters to a gif
// Commands
//   `!(tex|latex) <TEXT>` - Converts text to LaTeX
//   `$$<TEXT>$$` - Converts text to LaTeX

var request = require("request");

module.exports = function(robot){
  robot.hear(/\$\$([^\$]+)\$\$/, function(res){
    var regexString = res.match[1] || res.match[2] || res.match[3];
    res.send("http://latex.codecogs.com/gif.latex?" + encodeURIComponent(regexString));
    robot.superHackyPostImageToYaBoisChat(res.message.room, res.match[1])
  });

  robot.hear(/!(tex|latex) ([^\$]+)/, function(res){
    var regexString = res.match[2];
    res.send("http://latex.codecogs.com/gif.latex?" + encodeURIComponent(regexString));
    robot.superHackyPostImageToYaBoisChat(res.message.room, res.match[1])
  });

  robot.superHackyPostImageToYaBoisChat = function(channel, text) {
    var token = HUBOT_SLACK_TOKEN;
    channel = encodeURIComponent(channel);
    var urlBase= 'http://latex.codecogs.com/png.latex?%5Cdpi%7B300%7D%20'+encodeURIComponent(text);
    var dURL = "https://slack.com/api/chat.postMessage?token="+token+"&channel="+channel+"&text=%20&attachments=%5B%7B%22fallback%22%3A%22.%22%2C%22color%22%3A%20%22%2336a64f%22%2C%22image_url%22%3A%22" + encodeURIComponent(urlBase)+"%22%7D%5D&pretty=1";
    request(dURL);
  }
};
