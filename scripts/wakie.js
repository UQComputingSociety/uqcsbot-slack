// Description
//   Wakie Wakie - Pings a random person in #general and asks what they are up to
//

var HubotCron = require('hubot-cronjob');

module.exports = function(robot) {
	var fn, pattern, timezone;
	pattern = '0 17 * * *'; // Daily at 5:00PM
	timezone = 'Australia/Brisbane';

	fn = function() {
		robot.adapter.client.web.users.list(0, function(result){
            var members = result.members.filter(function (user) { return user.deleted == false; });
            var victim = members[Math.floor(Math.random() * active.length)];
            return robot.messageRoom("general", "Hey <@" + victim + ">! Tell us about something cool you are working on!");
        });
	};
	return new HubotCron(pattern, timezone, fn);
};
