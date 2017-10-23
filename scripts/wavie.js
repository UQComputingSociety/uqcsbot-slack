// Description
//   Wave at people as they joining/leaving a room

module.exports = function (robot) {
    // Wave at the person joining/leaving the room
    function wave(room) {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.web) {
            return;
        }

        // Shorten web client so we can have nice concise lines ;)
        var webClient = robot.adapter.client.web;

        // If room was not a channel (public) and not a group (private), exit
        if (room[0] != 'C' && room[0] != 'G') {
            return;
        }

        // Retrieve the room information and :wave: if the latest message is a person joining/leaving
        var channelPromise = (room[0] == 'C') ? webClient.channels.info(room) : webClient.groups.info(room);
        channelPromise.then(res => {
            // If the latest message was not a person joining nor leaving, exit
            if (res.channel.latest.subtype != 'channel_join' && res.channel.latest.subtype != 'channel_leave') {
                return;
            }

            webClient.reactions.add('wave', {channel: room, timestamp: res.channel.latest.ts});
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
