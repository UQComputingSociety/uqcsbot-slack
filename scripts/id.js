// Description
//   Get slack user ID
//
// Commands:
//   !`id` - Shows your slack user id
//
//
module.exports = function (robot) {
    robot.respond(/!?id/i, function(res) {
        res.send(res.envelope.user.id);
    });
    
    robot.respond(/!?whoami/i, function(res) {
        res.send("```" + JSON.stringify(robot.brain.userForId(res.envelope.user.id), null, 4) + "```");
    });
};
