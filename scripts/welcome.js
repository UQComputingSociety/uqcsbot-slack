// Description
//   Welcomes new users to UQCS Slack
//
"use strict";
var welcomeMessages = [
    "Hey there! Welcome to the UQCS slack!",
    "This is the first time I've seen you, so you're probably new here",
    "I'm UQCSbot, your friendly (open source) robot helper",
    "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with many subject-specific ones",
    "Your friendly admins are @trm, @dmarj97, @cat, @gricey, @csa, @ainz, and @mcoot",
    "Type \"help\" here, or \"uqcsbot help\" anywhere else to find out what I can do.",
    "and again, welcome :)"
];

function sendWelcome(robot, user, msg_id){
  if (msg_id == undefined) msg_id = 0;
  if (msg_id >= welcomeMessages.length) return;
  setTimeout(function () {
    robot.send({ room: user.id }, welcomeMessages[msg_id]);
	sendWelcome(robot, user, msg_id+1);
  }, messageTime);
}


//The time between each individual welcome message send
var messageTime = 2500;
module.exports = function (robot) {
    if(robot.adapter.client && robot.adapter.client.rtm) {
      var channel = robot.adapter.client.rtm.dataStore.getChannelByName("general");
      robot.enter(function (res) {
          if (res.message.room == channel.id) {
              var active = robot.adapter.client.web.users.list({presence: 0}, function(result){
                  var members = result.members.filter(function (user) { return user.deleted == false; });
                  if (members.length % 50 == 0) {
                      setTimeout(function () {
                          res.send(":tada: " + members.length + " members! :tada:");
                      }, messageTime);
                  }
                  var url = "https://http.cat/" + members.length;
                  robot.http(url).get()(function (err, resp, body) {
                      if (!err && resp.statusCode === 200) {
                          res.send(url);
                      }
                  });
              });
              res.send("Welcome, " + res.message.user.name + "!");
                          sendWelcome(robot, res.message.user);
          }
      });
    }
};

