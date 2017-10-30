// Description
//   Collects and yields general slack statistics for analysis and insight
//
// Commands:
//   `!stats (rooms|commands|<STAT>)` - Yields general slack statistics for analysis and insight
//   `!stats (subscribe|unsubscribe) (rooms|commands|<STAT>)` - Subscribes/Unsubscribes the user to/from the given stat. Subscriptions publish weekly results to subscribers

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

// Add item to set, first setting as a Set if one does not exist
// Returns true if successfully added a unique item, else false
function addToSet(map, entry, item) {
    if (!(entry in map)) map[entry] = new Set();
    if (map[entry].has(item)) return false;
    map[entry].add(item);
    return true;
}

// Removes item from set, returning true if successful else false
function removeFromSet(map, entry, item) {
    if (!(entry in map)) return false;
    return map[entry].delete(item);
}

// Returns a sorted list of object entries in descending order
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
        // If the stat is a private one, skip it
        if (s[0] == '_') {
            continue;
        }

        // If the attribute is the stat we're looking for, return it and its value
        var v = stats[s];
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
    // If no stat specified, exit
    var index = stat.indexOf(' ');
    if (index < 0) {
        return;
    }

    // Try subscribing to the stat
    var stat = stat.substring(index + 1);
    if (addToSet(subscribers, user.id, stat)) {
        var subscriptions = Array.from(subscribers[user.id]);
        var message = `Subscribed to \`${stat}\`, you are now subscribed to \`${subscriptions.join(', ')}\``;
    } else {
        var subscriptions = Array.from(subscribers[user.id]);
        var message = `Already subscribed to \`${stat}\`, you are currently subscribed to \`${subscriptions.join(', ')}\``;
    }
    robot.send({room: user.id}, message);
}

// Unsubscribes the user from the requested stat
function unsubscribeFromStat(robot, user, subscribers, stat) {
    // If no stat specified, exit
    var index = stat.indexOf(' ');
    if (index < 0) {
        return;
    }

    // Try unsubscribing from the stat
    var stat = stat.substring(index + 1);
    if (removeFromSet(subscribers, user.id, stat)) {
        var subscriptions = Array.from(subscribers[user.id]);
        var message = `Unsubscribed from \`${stat}\`, `;
        if (subscriptions.length > 0) {
            message += `you are still subscribed to \`${subscriptions.join(', ')}\``;
        } else {
            message += `you have no remaining subscriptions`;
        }
    } else {
        var subscriptions = Array.from(subscribers[user.id]);
        var message = `Could not find requested subscription \`${stat}\`, `;
        if (subscriptions.length > 0) {
            message += `you are currently subscribed to \`${subscriptions.join(', ')}\``;
        } else {
            message += `you have no current subscriptions`;
        }
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
        var message = `>>> _${totalMessages} total message(s) in ${sortedRooms.length} room(s)_\n\n`;
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
    if (!!statEntry) {
        var message = `>>>*${statEntry[0]}*: ${statEntry[1]}`;
    } else {
        var message = `Could not find requested stat \`${stat}\``;
    }
    robot.send({room: user.id}, message);
}

// Sends out all subscriber's subscriptions
function sendToSubscribers(robot, stats) {
    var subscribers = stats._subscribers;
    for (var subscriber in subscribers) {
        var user = {id: subscriber};
        var subscriptions = Array.from(subscribers[subscriber]);
        var message = `Here are your weekly subscriptions to \`${subscriptions.join(', ')}\`!`;
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
        var stats = getStats(robot);
        sendToSubscribers(robot, stats);

        // Reset stats
        for (var stat in stats) {
            if (stat == '_subscribers') continue;
            stats[stat] = {};
        }
    });
};

