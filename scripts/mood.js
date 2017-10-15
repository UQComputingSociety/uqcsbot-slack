// Description
//   Keeps track of user moods
//
// Commands:
//   `!mood` <USER NAME> - Outputs the mood of the user
//   `!happiest` - Outputs the happiest person
//   `!saddest` - Outputs the saddest person
//

var HubotCron = require('hubot-cronjob');

module.exports = function (robot) {
	var happy_emotes = [":\\)", ":D", ":3", ":>", ":'\\)",
		":grinning:", ":grin:", ":joy:", ":smiley:", ":smile:", ":laughing:",
		":wink:", ":blush:", ":slightly_smiling_face:", ":upside_down_face:",
		":relaxed:", ":yum:", ":heart_eyes:", ":kissing_heart:", ":kissing_smiling_eyes:",
		":stuck_out_tongue_winking_eye:", ":stuck_out_tongue_closed_eyes:",
		":stuck_out_tongue:", ":money_mouth_face:", ":hugging_face:", ":smirk:"];
	var sad_emotes = [":\\(", ":'\\(", ":<", 
		":unamused:", ":disappointed:", ":slightly_frowning_face:", ":white_frowning_face:",
		":persevere:", ":confounded:", ":tired_face:", ":weary:", ":frowning:",
		":anguished:", ":cry:", ":sob:"];

	function get_regex(arr) {
		var combined = "(";
		for(var i = 0; i < arr.length - 1; i++) {
			combined += arr[i];
			combined += "|";
		}
		combined += arr[arr.length - 1];
		combined += ")";
		return new RegExp(combined, "i");
	}

	robot.hear(get_regex(sad_emotes), function (res) {
		var moods = robot.brain.get("moods");
		if(moods === null) {
			robot.brain.set("moods", {});
			moods = robot.brain.get("moods");
			if(moods === null) { return; }
		}
		var name = res.message.user.name.toLowerCase();
		if(moods[name] === undefined) {
			moods[name] = -1;
		}else {
			moods[name]--;
		}
	});

	robot.hear(get_regex(happy_emotes), function (res) {
		var moods = robot.brain.get("moods");
		if(moods === null) {
			robot.brain.set("moods", {});
			moods = robot.brain.get("moods");
			if(moods === null) { return; }
		}
		var name = res.message.user.name.toLowerCase();
		if(moods[name] === undefined) {
			moods[name] = 1;
		}else {
			moods[name]++;
		}
	});

	robot.respond(/!?mood ?(.+)?/i, function(res) {
		var moods = robot.brain.get("moods");
		if(moods === null) {
			res.send("Brain not loaded.\r\n");
			return;
		}

		var target;
		if(res.match[1]) {
			target = res.match[1].toLowerCase();
		}else {
			target = res.message.user.name.toLowerCase();
		}
		if(moods[target] === undefined) {
			res.send(target + " is emotionless...\r\n");
		}else {
			if(moods[target] == 0) {
				res.send(target + " is neutral.\r\n");
			}else if(moods[target] > 0) {
				res.send(target + " is happy!\r\n");
			}else {
				res.send(target + " is sad... Try cheer them up!\r\n");
			}
		}
	});

	robot.respond(/!?(happiest|saddest)/i, function(res) {
		var moods = robot.brain.get("moods");
		if(moods === null) {
			res.send("Brain not loaded.\r\n");
			return;
		}

		var max;
		var min;
		var m = moods;
		for(var p in m) {
			if(max === undefined || m[p] > m[max]) { max = p; }
			if(min === undefined || m[p] < m[min]) { min = p; }
		}

		if(res.match[1] === "happiest") {
			res.send(max + " was the happest! YAY " + max + "!!!\r\n");
		}else {
			res.send(min + " was the saddest... Poor " + min + "... Everybody try cheer them up!\r\n");
		}
	});

	return new HubotCron("0 0 * * *", "Australia/Brisbane", function() {
		robot.brain.set("moods", {});
	});
};
