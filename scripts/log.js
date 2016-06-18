// Description
//   Logs messages of channels
//
// Commands:
//   !`logging` <status|enable|disable> <channel> - Manages channel logging
//
module.exports = function (robot) {
	reset_brain = function() {
		robot.brain.set("channel_logs", {
			enabled: [],
			messages: {}
		});
	};

	robot.hear(/(.+)/, function (res) {
		var logs = robot.brain.get("channel_logs");
		if(logs === null) {
			reset_brain();
			if(logs === null) { return; }
		}

		var channel = res.room;
		if(logs.enabled.indexOf(channel) === -1) { return; } // Not logging

		if(logs.messages[channel] === undefined) {
			logs.messages[channel] = [];
		}

		logs.messages[channel].push({msg: res.match[1], res: res});
	});

	robot.respond(/!?logging (status|enable|disable) ?(#.+)?/i, function(res) {
		var logs = robot.brain.get("channel_logs");
		if(logs === null) {
			res.send("Brain not loaded.\r\n");
			return;
		}

		var cmd = res.match[1].toLowerCase();
		var channel = res.match[2];
		if(channel === undefined) {
			channel = res.room;
		}else {
			channel = channel.substring(1, channel.length).toLowerCase();
		}

		var logging_enabled = (logs.enabled.indexOf(channel) !== -1);

		if(cmd === "status") {
			res.send("Logging in #" + channel + " is " + (logging_enabled ? "enabled" : "disabled") + "\r\n");
		}else if(cmd === "enable") {
			if(logging_enabled) {
				res.send("Already enabled.\r\n");
			}else {
				logs.enabled.push(channel);
				robot.messageRoom("#" + channel, res.message.user.name + " has enabled logging in this channel!\r\n");
			}
		}else if(cmd === "disable") {
			if(!logging_enabled) {
				res.send("Already disabled.\r\n");
			}else {
				logs.enabled.splice(logs.enabled.indexOf(channel), 1);
				robot.messageRoom("#" + channel, res.message.user.name + " has disabled logging in this channel!\r\n");
			}
		}
	});
};
