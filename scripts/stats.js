// Description
//   Collects and yields general slack statistics for analysis and insight
//
// Commands:
//   `!stats (rooms|commands|<STAT>)` - Yields general slack statistics for analysis and insight
//   `!stats (subscribe|unsubscribe) (rooms|commands|<STAT>)` - Subscribes/Unsubscribes user from the given stats

var HubotCron = require('hubot-cronjob');

// Default stats upon reset
DEFAULT_STATS = {rooms: {}, commands: {}, _subscribers: {}};

/////////////////////
// HELPER COMMANDS //
/////////////////////

// Increment counter in map, first setting to 0 if it does not exist
function incrementCounter(map, entry) {
    if (!(entry in map)) map[entry] = 0;
    map[entry]++;
}

// Add item to list, first setting as list if one does not exist
function addToList(map, entry, item) {
    if (!(entry in map)) map[entry] = [];
    map[entry].push(item);
}

// Removes item from list, returning true if successful else false
function removeFromList(map, entry, item) {
    if (!(entry in map)) return false;
    var index = map[entry].indexOf(item);
    if (index == -1) return false;
    map[entry].splice(index, 1);
    return true;
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

// Returns the requested stat, else null
function getStat(stats, stat) {
    // Loop over object attributes
    for (var s in stats) {
        var v = stats[s];
        // If the attribute is the stat we're looking for, return it and its value
        if (s == stat) {
            return [s, v]
        }

        // If the value is another object, recurse into it
        if (typeof v === 'object') {
            result = getStat(v, stat);
            if (!!result) {
                return result;
            }
        }
    }
    return null;
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
    // If the command is not actually a command or the room is a private channel, exit
    var command = res.message.text;
    var room = res.message.room;
    if ((command[0] != '!' && room[0] != 'D') || room[0] == 'G') {
        return;
    }

    // If we're talking to uqcsbot, remove the implicit uqcsbot call
    if (command.indexOf('uqcsbot') == 0) {
        command = command.replace('uqcsbot ', '');
    }

    // Strip down to just the base command
    var baseCommand = command.split(' ')[0];
    incrementCounter(stats.commands, baseCommand);
}

// Subscribes the user to the requested stat
function subscribeToStat(robot, user, subscribers, stat) {
    var stat = stat.replace('subscribe ', '');
    addToList(subscribers, user.id, stat);
    message = `Subscribed to \`${stat}\`, ` +
              `you are now subscribed to \`${subscribers[user.id].join(', ')}\``;
    robot.send({room: user.id}, message);
}

// Unsubscribes the user from the requested stat
function unsubscribeFromStat(robot, user, subscribers, stat) {
    var stat = stat.replace('unsubscribe ', '');
    var message = `Could not find requested subscription \`${stat}\``;
    if (removeFromList(subscribers, user.id, stat)) {
        message = `Unsubscribed from \`${stat}\`, ` +
                  `you are now subscribed to \`${subscribers[user.id].join(', ')}\``;
    }
    robot.send({room: user.id}, message);
}

////////////////////
// PRINT COMMANDS //
////////////////////

// Prints out command stat
function printCommandStat(robot, user, commands) {
    // Get a sorted list of commands and calculate the total amount of calls
    var sortedCommands = getSortedEntries(commands);
    var totalCalls = sortedCommands.reduce((sum, entry) => sum + entry[1], 0);

    // Build and send output message
    var message = `>>> _${totalCalls} total call(s)_\n\n`;
    sortedCommands.forEach(commandEntry => {
        percentage =  Math.round(commandEntry[1] / totalCalls * 100);
        message += `*${commandEntry[0]}*: ${commandEntry[1]} call(s) \`(${percentage}%)\`\n`;
    });
    robot.send({room: user.id}, message);
}

// Prints out room stat
function printRoomStat(robot, user, rooms) {
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
            percentage =  Math.round(roomEntry[1] / totalMessages * 100);
            message += `*${roomEntry[0]}*: ${roomEntry[1]} message(s) \`(${percentage}%)\`\n`; 
        })
        robot.send({room: user.id}, message);
    }).catch(err => console.log(err));
}

// Prints out requested stat
function printStat(robot, user, stats, stat) {
    var statEntry = getStat(stats, stat);
    var message = `Could not find requested stat \`${stat}\``;
    if (!!statEntry) {
        message = `>>>*${statEntry[0]}*: ${statEntry[1]}`;
    }
    robot.send({room: user.id}, message);
}

// Sends out all subscriber's subscriptions
function sendToSubscribers(robot) {
    var stats = getStats(robot);
    var subscribers = stats._subscribers;
    for (var subscriber in subscribers) {
        var user = {id: subscriber};
        var subscriptions = subscribers[subscriber];
        message = `Here are your weekly subscriptions to \`${subscriptions.join(', ')}\`!`;
        robot.send({room: subscriber}, message)[0].then(() => {
            subscriptions.forEach(subscription => {
                switch (subscription) {
                    case 'rooms':    printRoomStat(robot, user, stats.rooms);       break;
                    case 'commands': printCommandStat(robot, user, stats.commands); break;
                    default:         printStat(robot, user, stats, subscription);
                }
            });
        });
    }
}

///////////////
// LISTENERS //
///////////////

module.exports = function (robot) {
    // Listen to everything (._.)
    robot.hear(/.*/, function (res) {
        var stats = getStats(robot);
        handleRoomStat(stats, res);
        handleCommandStat(stats, res);
    });

    // Listen to command calls
    robot.respond(/!?stats (.*)/i, function (res) {
        var stats = getStats(robot);
        var option = res.match[1];
        var user = res.message.user;
        switch(option.split(' ')[0]) {
            case 'rooms':       printRoomStat(robot, user, stats.rooms);                      break;
            case 'commands':    printCommandStat(robot, user, stats.commands);                break;
            case 'subscribe':   subscribeToStat(robot, user, stats._subscribers, option);     break;
            case 'unsubscribe': unsubscribeFromStat(robot, user, stats._subscribers, option); break;
            default:            printStat(robot, user, stats, option);
        }
    });

    // Send out weekly results to subscribers and reset stats
    return new HubotCron("0 0 * * 1", "Australia/Brisbane", function() {
        sendToSubscribers(robot);
        robot.brain.set("stats", DEFAULT_STATS);
    });
};

