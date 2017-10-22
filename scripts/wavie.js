// Description
//   Wave people as they enter and exit the room

module.exports = function (robot) {
    // Wave at the latest message in the room
    function wave(room) {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.web) {
            return;
        }

        // Shorten web client so we can have nice concise lines :)
        webClient = robot.adapter.client.web;

        // Try channel as a public channel search first, then as a private channel
        webClient.channels.info(room)
            .then(res => webClient.reactions.add('wave', {channel: room, timestamp: res.channel.latest.ts}))
            .catch(err => { if (err == 'channel_not_found') return webClient.groups.info(room); })
            .then(res => webClient.reactions.add('wave', {channel: room, timestamp: res.channel.latest.ts}))
            .catch(err => console.log);
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
