// Description
//   Restricts channel and everyone pinging to predefined people
//   Stops people from pinging everyone out of ignorance (mostly)
//   This command works for anyone in channels with less that 50 people
//   
// Commands:
//   !`ping` (channel|everyone|here)

// Dictionary of characters mapping to emojis.
var allowed = ['trm', 'dmarj97', 'csa', 'mqt', 'ainz', 'gricey', 'cat'];

module.exports = function (robot) {
    robot.respond(/!?ping ?(.+)?$/i, function (res) {
        if (robot.adapter.client && robot.adapter.client.rtm) {
            // Get text, all in lowercase and remove non alphanumeric
            var msg = res.match[1].toLowerCase().replace(/[^a-zA-Z0-9]/g, "");
            var room = res.message.room;
	    var channel = robot.adapter.client.rtm.dataStore.getChannelGroupOrDMById(room);

            if (in_array(res.message.user.name, allowed) ||
                channel.members.length < 50) {
                if (msg === "channel") {
                    res.send("@channel");
                }
                else if (msg === "everyone") {
                    res.send("@everyone");
                }
                else if (msg === "here") {
                    res.send("@here");
                }
            }
        }
    });

    function in_array(str, array) {
        for (var i = 0; i < array.length; i++) {
            if (str.toLowerCase() === array[i].toLowerCase()) {
                return true;
            }
        }
        return false;
    }
};
