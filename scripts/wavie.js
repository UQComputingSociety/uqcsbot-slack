// Description
//   Wave at people as they join/leave a room

module.exports = function (robot) {
    // Wave at the person joining/leaving the room
    function wave(roomId) {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.rtm || !robot.adapter.client.web) {
            return;
        }

        // Get room info from data store
        var room = robot.adapter.client.rtm.dataStore.getChannelById(roomId);

        // If user entered announcements, don't wave at them and exit
        if (room.name == 'announcements') {
            return;
        }

        // If there was no last message or the last message was not a person joining nor leaving, exit
        var latest = room.latest;
        if (!latest || (latest.subtype != 'channel_join' && latest.subtype != 'channel_leave')) {
            return;
        }

        // :wave:!
        robot.adapter.client.web.reactions.add('wave', {channel: room.id, timestamp: latest.ts});
    }

    // Listen for when someone enters/exits a room
    robot.enter(res => wave(res.message.room));
    robot.leave(res => wave(res.message.room));
};
