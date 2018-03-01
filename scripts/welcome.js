// Description
//   Welcomes new users to UQCS Slack and check for member milestones

var MEMBER_MILESTONE = 50;  // Number of members between posting a celebration
var MESSAGE_PAUSE = 2500;   // Number of seconds between sending bot messages
var WELCOME_MESSAGES = [    // Welcome messages sent to new members
    "Hey there! Welcome to the UQCS slack!",
    "This is the first time I've seen you, so you're probably new here",
    "I'm UQCSbot, your friendly (open source) robot helper",
    "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with many subject-specific ones",
    "Your friendly admins are @trm, @mitch, @rob, @mb, @csa, @guthers, and @artemis",
    "Type \"help\" here, or \"!help\" anywhere else to find out what I can do!",
    "and again, welcome :)"
];

module.exports = function (robot) {
    robot.enter(function (res) {
        // Make sure we have access to all the clients we need
        if(!robot.adapter.client || !robot.adapter.client.rtm || !robot.adapter.client.web) {
            return;
        }

        // Check if user has entered #announcements channel
        var announcements = robot.adapter.client.rtm.dataStore.getChannelByName("announcements"); 
        if (res.message.room != announcements.id) {
            return;
        }
        
        // Welcome new user to #general
        var general = robot.adapter.client.rtm.dataStore.getChannelByName("general").id; 
        name = res.message.user.profile.display_name || res.message.user.name;
        robot.send({room: general}, "Welcome " + name + "!")[0]
            .then(res => robot.adapter.client.web.reactions.add('wave', {channel: general, timestamp: res.ts}));

        // Welcome new user personally
        WELCOME_MESSAGES.forEach((message, i) => setTimeout(() => {
            robot.send({room: res.message.user.id}, message);
        }, i * MESSAGE_PAUSE));


        // If we're not at a member milestone, don't bother celebrating!
        var activeMembers = announcements.members.filter(user => !user.deleted);
        if (activeMembers.length % MEMBER_MILESTONE != 0) {
            return;
        }

        res.send(":tada: " + activeMembers.length + " members! :tada:");
    });
};
