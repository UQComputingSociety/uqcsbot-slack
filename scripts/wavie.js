// Description
//   Wave at people as they join/leave a room

module.exports = function (robot) {
    // Wave at the person joining/leaving the room
    function wave(room) {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.web) {
            return;
        }

        // If user entered announcements, don't wave at them
        var announcements = robot.adapter.client.rtm.dataStore.getChannelByName("announcements").id; 
        if (room == announcements) {
            return;
        }

        // Shorten web client so we can have nice concise lines ;)
        var webClient = robot.adapter.client.web;

        // If room was not a public channel and not a private channel, exit
        if (room[0] == 'C') {
            var channelPromise = webClient.channels.info(room);
        } else if (room[0] == 'G') {
            var channelPromise = webClient.groups.info(room);
        } else {
            return;
        }

        // :wave: if the latest message is a person joining/leaving
        channelPromise.then(res => {
            // If the last message was not a person joining nor leaving, exit
            var last = res.channel.latest;
            if (last.subtype != 'channel_join' && last.subtype != 'channel_leave') {
                return;
            }

            return webClient.reactions.add('wave', {channel: room, timestamp: last.ts});
        }).catch(err => console.log);
    }

    // Listen for when someone enters a room
    robot.enter(function (res) {
        wave(res.message.room);
    });

    // Listen for when someone leaves a room
    robot.leave(function (res) {
        wave(res.message.room);
    });
};
