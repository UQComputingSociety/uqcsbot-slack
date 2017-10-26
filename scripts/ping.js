// Description
//   Restricts channel and everyone pinging to predefined people
//   Stops people from pinging everyone out of ignorance (mostly)
//   This command works for anyone in channels with less that 50 people
//   
// Commands:
//   `!ping (channel|everyone|here)` - Pings channel/everyone/here only if the user is an admin OR the channel contains less than 50 people

module.exports = function (robot) {
    robot.respond(/!?ping ?(.+)?$/i, function (res) {
        if (robot.adapter.client && robot.adapter.client.rtm) {
            // Get text, all in lowercase and remove non alphanumeric
            var msg = res.match[1].toLowerCase().replace(/[^a-zA-Z0-9]/g, "");
            var room = res.message.room;
            var user = res.message.user;
            var data = robot.adapter.client.rtm.dataStore;
            var channel = data.getChannelGroupOrDMById(room);

            if (user.is_admin || channel.members.length < 50) {
                if (msg === "channel") {
                    res.send("@channel");
                }
                else if (msg === "everyone") {
                    res.send("@everyone");
                }
                else if (msg === "here") {
                    res.send("@here");
                }
            } else {
                res.send("Unauthorised ping, must be either admin or in a channel with < 50 members")
            }
        }
    });


    function adminSend(channel, msg) {
        SLACK_ADMIN_TOKEN = process.env.SLACK_ADMIN_TOKEN;

        var prefix = "https://slack.com/api/chat.postMessage?"
        var token = "token=" + SLACK_ADMIN_TOKEN + "&"
        var channel = "channel=" + channel + "&"
        var text = "text=" + msg;
        var request = prefix + token + channel + text;
    }
};
