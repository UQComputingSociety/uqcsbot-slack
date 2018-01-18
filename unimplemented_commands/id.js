// Description
//   Get slack user ID
//
// Commands:
//   `!id` - Returns the user's slack ID
//   `!whoami` - Returns slack information about the user

module.exports = function (robot) {
    robot.respond(/!?id/i, function(res) {
        res.send(res.envelope.user.id);
    });
    
    robot.respond(/!?whoami/i, function(res) {
        res.send("```" + JSON.stringify(robot.brain.userForId(res.envelope.user.id), null, 4) + "```");
    });
};
