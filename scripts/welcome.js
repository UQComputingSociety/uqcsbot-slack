// Description
//   Welcomes new users to UQCS Slack

var MESSAGE_PAUSE = 2500;
var WELCOME_MESSAGES = [
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
        if(!robot.adapter.client || !robot.adapter.client.rtm || !robot.adapter.client.web) {
            return;
        }

        var general = robot.adapter.client.rtm.dataStore.getChannelByName("general").id; 
        if (res.message.room != general) {
            return;
        }
        
        res.send("Welcome, " + res.message.user.name + "!");
        WELCOME_MESSAGES.map((message, i) => setTimeout(() => {
            robot.send({room: res.message.user.id}, message);
        }, i * MESSAGE_PAUSE));

        robot.adapter.client.web.users.list({presence: false}).then(result => {
            var members = result.members.filter(user => user.deleted == false);
            if (members.length % 50 != 0) {
                return;
            }

            res.send(":tada: " + members.length + " members! :tada:");
        });
    });
};
