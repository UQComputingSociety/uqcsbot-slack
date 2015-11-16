// Description
//   Allows users to store and bring out reaction images/gifs
// 
// Commands:
//   !mrw <reaction_string>
// 	 uqcsbot new reaction <reaction_string> <url to reaction image>
// 

module.exports = function (robot) {
  robot.hear(/^!mrw (.+)/i, function (res) {
	  var rStr = res.match[1];
	  if(!rStr) return;
	  robot.showReaction(rStr, res)
  });
  
  robot.hear(/^uqcsbot new reaction (\w+\ [^ \n]+)/i ), function (res) {
    var rStr = res.match[3];
    var url = res.match[4];
    if(!url || !rStr) return;
    robot.storeReaction(rStr, url, res);
  }
	
  robot.showReaction = function(reactionString, res) {
    var reactionDict = robot.brain.get('superSecretReactionKeyStoreThing');
    if(reactionDict[reactionString]) {
      res.send(reactionDict[reactionString]);
      return;
    }
    res.reply("\""+reactionString+"\" isn't a valid reaction yet :'(");
    res.reply("You can add it though with \"uqcsbot new reaction <reaction_string> <url to image>\"");
  }
  
  robot.storeReaction = function(reactionString, reactionURL, res) {
    var reactionDict = robot.brain.get('superSecretReactionKeyStoreThing');
    if(reactionDict[reactionString]) {
      res.reply("That reaction is already tied to an image!");
      return;
    }
    reactionDict[reactionString] = reactionURL;
  }
}