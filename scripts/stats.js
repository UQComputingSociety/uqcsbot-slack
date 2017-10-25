// Description
//   TODO
//
// Commands:
//   `!stats (channels|commands)` - TODO

// Default stats upon reset
DEFAULT_STATS = {channels: {}, commands: {}};

// Retrieves stored slack stats, setting them to default values if none are currently stored
function getStats(robot) {
    var stats = robot.brain.get('stats');
    if (!stats) {
        robot.brain.set('stats', DEFAULT_STATS);
        stats = robot.brain.get('stats');
    }
    return stats;
}

module.exports = function (robot) {
    robot.hear(/.*/, function (res) {
        var stats = getStats(robot);

        // Increment channel message counter, setting to 0 if it does not exist
        var room = res.message.room;
        if (!(room in stats.channels)) {
            stats.channels[room] = 0;
        }
        stats.channels[room]++;

        // If the message is not a command, exit
        if (res.message.text[0] != '!') {
            return;
        }

        // Increment command usage counter, setting to 0 if it does not exist
        var command = res.message.text;
        if (!(command in stats.commands)) {
            stats.commands[command] = 0;
        }
        stats.commands[command]++;
    });

    robot.respond(/!?stats (channels|commands)/, function (res) {
        var stats = getStats(robot);

        option = res.match[1];
        if (option == 'channels') {
            console.log(stats.channels);
        }

        if (option == 'commands') {
            console.log(stats.commands);
        }
    });
};