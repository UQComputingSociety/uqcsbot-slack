// Description
//   Welcomes new users to UQCS Slack
//
"use strict";
var welcomeMessages = [
    "Hey there! Welcome to the UQCS slack!",
    "This is the first time I've seen you, so you're probably new here",
    "I'm UQCSbot, your friendly (open source) robot helper",
    "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with many subject-specific ones",
    "Your friendly admins are @trm, @svict4, @gricey, @csa, @ainz, @dmarj97",
    "Type \"help\" here, or \"uqcsbot help\" anywhere else to find out what I can do.",
    "and again, welcome :)"
];
//The time between each individual welcome message send
var messageTime = 2500;
module.exports = function (robot) {
    robot.enter(function (res) {
        if (res.message.room == "general") {
            var members = 99999999999;
            res.send("Welcome, " + res.message.user.name + "!");
            var url = "https://http.cat/" + members;
            robot.http(url).get()(function (err, resp, body) {
                if (!err && resp.statusCode === 200) {
                    res.send(url);
                }
            });
            if (members % 50 == 0) {
                setTimeout(function () {
                    res.send(":tada: " + members + " members! :tada:");
                }, messageTime);
            }
            welcomeMessages.forEach(function (msg, i) {
                setTimeout(function () {
                    robot.send({ room: res.message.user.name }, msg);
                }, messageTime * i);
            });
        }
    });
};
