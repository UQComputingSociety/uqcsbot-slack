// Description
//   Collects and yields general slack statistics for analysis and insight
//
// Commands:
//   `!stats (rooms|commands)` - Yields general slack statistics for analysis and insight

// Default stats upon reset
DEFAULT_STATS = {rooms: {}, commands: {}};

/////////////////////
// HELPER COMMANDS //
/////////////////////

// Increment counter in map, first setting to 0 if it does not exist
function incrementCounter(map, entry) {
    if (!(entry in map)) {
        map[entry] = 0;
    }
    map[entry]++;
}

// Returns a sorted list of object entries
function getSortedEntries(object) {
    var entries = [];
    for (var entry in object) entries.push([entry, object[entry]])
    return entries.sort((a, b) => b[1] - a[1]);
}

// Retrieves stored slack stats, setting them to default values if they do not exist
function getStats(robot) {
    var stats = robot.brain.get('stats');
    if (!stats) {
        robot.brain.set('stats', DEFAULT_STATS);
        stats = robot.brain.get('stats');
    }
    return stats;
}

//////////////////////
// HANDLER COMMANDS //
//////////////////////

// Handles room stat
function handleRoomStat(stats, res) {
    // If room is not a public channel, exit
    var room = res.message.room;
    if (room[0] != 'C') return;
    incrementCounter(stats.rooms, room);
}

// Handles command stat 
function handleCommandStat(stats, res) {
    // If the command is not actually a command, exit
    var command = res.message.text;
    if (command[0] != '!') {
        return;
    }

    incrementCounter(stats.commands, command);

    // If command did not contain any options, exit
    var baseCommand = command.split(' ')[0];
    if (baseCommand == command) {
        return;
    }

    incrementCounter(stats.commands, baseCommand);
}

////////////////////
// PRINT COMMANDS //
////////////////////

// Prints out command stat
function printCommandStat(robot, res, commands) {
    // Get a sorted list of commands and calculate the total amount of calls
    var sortedCommands = getSortedEntries(commands);
    var totalCalls = sortedCommands.reduce((sum, entry) => {
        // Make sure we only count base commands
        if (entry[0].indexOf(' ') < 0) return sum + entry[1];
        return sum;
    }, 0);

    // Build and send output message
    var message = `>>> _${totalCalls} total call(s)_\n\n`;
    sortedCommands.forEach(commandEntry => {
        message += `*${commandEntry[0]}*: ${commandEntry[1]} call(s)\n`; 
    });
    res.send(message);
}

// Prints out room stat
function printRoomStat(robot, res, rooms) {
    // Make sure we have access to all the clients we need
    if(!robot.adapter.client || !robot.adapter.client.web) {
        return;
    }

    // Get a sorted list of commands and calculate the total amount of calls
    var sortedRooms = getSortedEntries(rooms);
    var totalMessages = sortedRooms.reduce((sum, entry) => sum + entry[1], 0);

    // Generate a list of promises that resolve to a room's name and its # of calls
    var sortedRoomPromises = sortedRooms.map(roomEntry => {
        return robot.adapter.client.web.channels.info(roomEntry[0])
            .then(result => [result.channel.name, roomEntry[1]]);
    });

    // Attempt to resolve all promises to build and send output message
    Promise.all(sortedRoomPromises).then(sortedNamedRooms => {
        var message = `>>> _${totalMessages} total message(s)_\n\n`;
        sortedNamedRooms.forEach(roomEntry => {
            message += `*${roomEntry[0]}*: ${roomEntry[1]} message(s)\n`; 
        })
        res.send(message);
    }).catch(err => console.log(err));
}

///////////////
// LISTENERS //
///////////////

module.exports = function (robot) {
    robot.hear(/.*/, function (res) {
        var stats = getStats(robot);
        handleRoomStat(stats, res);
        handleCommandStat(stats, res);
    });

    robot.respond(/!?stats (rooms|commands)/, function (res) {
        var stats = getStats(robot);
        var option = res.match[1];
        if (option == 'rooms')    printRoomStat(robot, res, stats.rooms);
        if (option == 'commands') printCommandStat(robot, res, stats.commands);
    });
};
