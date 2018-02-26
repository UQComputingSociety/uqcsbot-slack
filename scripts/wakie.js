// Description
//   Wakie Wakie - Pings two random people in #general and asks what they are up to

var HubotCron = require('hubot-cronjob');

// List of reactions to wakie message with
var REACTS = ['waiting', 'apple_waiting', 'waiting_droid', 'keen', 'fiestaparrot']

module.exports = function(robot) {
    // Wakie function that pings two random people in general
    var wakieFunction = function() {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.web || !robot.adapter.client.rtm) {
            return;
        }

        // Send ping to two random victims in #general and react with random emoji
        var general = robot.adapter.client.rtm.dataStore.getChannelByName("general");
        var members = general.members.filter(user => !user.deleted && !user.is_bot);
        var victim1 = members[Math.floor(Math.random() * members.length * 0.5)];
        var victim2 = members[Math.floor(Math.random() * members.length * 0.5 + (members.length / 2))];
        var react   = REACTS[Math.floor(Math.random() * REACTS.length)];
        message = "Hey <@" + victim1 + ">! Tell us about something cool you are working on!\r\n" +
                  "Hey <@" + victim2 + ">! Tell us about something cool you are working on!";
        robot.send({room: general.id}, message)[0]
            .then(res => robot.adapter.client.web.reactions.add(react, {channel: general.id, timestamp: res.ts}));
    };

    // Export the cron job to run the wakie function at 5pm everyday
    return new HubotCron('0 17 * * *', 'Australia/Brisbane', wakieFunction);
};
