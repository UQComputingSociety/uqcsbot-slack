// Description
//   Generates help commands for UQCSbot
//
// Commands:
//   `!help` - Displays all of the help commands that UQCSbot knows about

module.exports = function (robot) {
    robot.respond(/!?help/i, function (res) {
        user = {room: res.message.user.id};
        commands = robot.helpCommands();
        robot.send(user, 'Here are my commands:\n\n>>>' + commands.join('\n'));
    });
};