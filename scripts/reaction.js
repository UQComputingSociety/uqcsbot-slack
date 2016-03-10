// Description
//  Allows users to store and bring out reaction images/gifs
// 
// Commands:
//  !mrw <reaction_string>
//  uqcsbot new reaction <reaction_string> <url to reaction image>
// 

module.exports = function (robot) {
	robot.respond(/!?mrw (.+)/i, function (res) {
		var rStr = res.match[1];
		if(!rStr) return;
		robot.showReaction(rStr, res)
	});

	robot.respond(/new reaction (\w+\ [^ \n]+)/i, function (res) {
		var input = res.match[1].split(" ");
		var rStr = input[0];
		var url = input[1]; // should probably ensure this is a url :/
		if(!url || !rStr) res.reply("lolwot");
		robot.storeReaction(rStr, url, res);
	});

	robot.showReaction = function(reactionString, res) {
		var reactionDict = robot.brain.get('superSecretReactionKeyStoreThing');
		if(reactionDict && reactionDict[reactionString]) {
			res.send(reactionDict[reactionString]);
			return;
		}
		res.reply("\""+reactionString+"\" isn't a valid reaction yet :'(");
		res.reply("You can add it though with \"uqcsbot new reaction <reaction_string> <url to image>\"");
	}

	robot.storeReaction = function(reactionString, reactionURL, res) {
		var reactionDict = robot.brain.get('superSecretReactionKeyStoreThing');
		if(!reactionDict) {
			reactionDict = {};
			robot.brain.set('superSecretReactionKeyStoreThing', reactionDict);
		}

		if(!reactionDict[reactionString]) {
			reactionDict[reactionString] = reactionURL;
			return;
		}

		res.reply("That reaction is already tied to an image!");
	}
}
