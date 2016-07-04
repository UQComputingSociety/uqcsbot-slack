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
};
