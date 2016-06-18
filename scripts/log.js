// Description
//   Logs messages of channels
//
//
module.exports = function (robot) {
	robot.brain.on("loaded", function() {
		robot.brain.set("channel_logs", {});
	});

	robot.hear(/(.+)/, function (res) {
		var logs = robot.brain.get("channel_logs");
		if(logs === null) { return; } // Brain not loaded

		var channel = res.room;

		if(logs[channel] === undefined) {
			logs[channel] = [];
		}

		logs[channel].append({msg: res.match[1], res: res});
	});
}
