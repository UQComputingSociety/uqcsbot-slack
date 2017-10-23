// Description
//   Wakie Wakie - Pings two random people in #general and asks what they are up to

var HubotCron = require('hubot-cronjob');

var API_LIMIT = 200;                 // Number of members to get at a time
var PATTERN =  '59 11 * * *';        // Daily at 5:00PM
var TIMEZONE = 'Australia/Brisbane'; // in B-town

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
        var announcements = robot.adapter.client.rtm.dataStore.getChannelByName("announcements").id;
        getMembers(robot, announcements, []).then(members => {
            var victim1 = members[Math.floor(Math.random() * members.length)];
            var victim2 = members[Math.floor(Math.random() * members.length)];
            robot.messageRoom("general", 
                "Hey <@" + victim1 + ">! Tell us about something cool you are working on!\r\n" + 
                "Hey <@" + victim2 + ">! Tell us about something cool you are working on!");
        });
    };

    // Export the cron job to run the wakie function at the specified time
    return new HubotCron(PATTERN, TIMEZONE, wakieFunction);
};
