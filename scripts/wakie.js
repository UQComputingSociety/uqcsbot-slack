// Description
//   Wakie Wakie - Pings a random person in #general and asks what they are up to
//

var HubotCron = require('hubot-cronjob');

module.exports = function(robot) {
	var fn, pattern, timezone;
	pattern = '0 17 * * *'; // Daily at 5PM
	timezone = 'Australia/Brisbane';

	fn = function() {
		var general = robot.adapter.client.getChannelGroupOrDMByName("general");
		var victim = general.members[Math.floor(Math.random() * general.members.length)];

		return robot.messageRoom("general", "Hey @" + victim.name + "! Tell us about something cool you are working on!");
	};
	return new HubotCron(pattern, timezone, fn);
};
