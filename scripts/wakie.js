// Description
//   Wakie Wakie - Pings two random people in #general and asks what they are up to

var HubotCron = require('hubot-cronjob');

var API_LIMIT = 200; // Number of members to get at a time
var PATTERN   = '0 17 * * *'; // Daily at 5:00PM
var TIMEZONE  = 'Australia/Brisbane';
var LOADING   = ['waiting', 'apple_waiting', 'waiting_droid', 'waitingparrot'] // List of waiting emojs to react with

// Get a list of all the members in a room
function getMembers(robot, room, members, cursor) {
    // No more members to get, return the final list
    if (cursor == "") {
        return Promise.resolve(members);
    }

    // Concat this batch of members and request for next batch
    return robot.adapter.client.web.conversations.members(room, {limit: API_LIMIT, cursor: cursor})
        .then(res => getMembers(robot, room, members.concat(res.members), res.response_metadata.next_cursor));
}

module.exports = function(robot) {
    // Wakie function that pings two random people in general
    var wakieFunction = function() {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.web || !robot.adapter.client.rtm) {
            return;
        }

        // Get all the members in #general and send ping two random victims, react with :loading:
        var general = robot.adapter.client.rtm.dataStore.getChannelByName("general").id;
        getMembers(robot, general, []).then(members => {
            var victim1 = members[Math.floor(Math.random() * members.length)];
            var victim2 = members[Math.floor(Math.random() * members.length)];
            var react   = LOADING[Math.floor(Math.random() * LOADING.length)];
            message = "Hey <@" + victim1 + ">! Tell us about something cool you are working on!\r\n" + 
                      "Hey <@" + victim2 + ">! Tell us about something cool you are working on!";
            robot.send({room: general}, message)[0]
                .then(res => robot.adapter.client.web.reactions.add(react, {channel: general, timestamp: res.ts}));
        });
    };

    // Export the cron job to run the wakie function at the specified time
    return new HubotCron(PATTERN, TIMEZONE, wakieFunction);
};
