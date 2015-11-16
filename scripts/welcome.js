// Description
//   Welcomes new users to UQCS Slack
// Commands:
//   hubot seen <user> - Finds out when I last saw someone
// 

var welcomeMessages = [
  "Hey there! Welcome to the UQCS slack!",
  "This is the first time I've seen you, so you're probably new here",
  "I'm UQCSbot, your friendly (open source) robot helper",
  "Introduce yourself on #intros, join some channels", 
  "We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with some subject-specific ones",
  "Your friendly admins are @trm, @svict4, @gricey, @rachcatch, @ainsleynand",
  "Type \"help\" here, or \"uqcsbot help\" anywhere else to find out what I can do.",
  "and again, welcome :)"
];

//The time between each individual welcome message send
var messageTime = 2500;


module.exports = function(robot){
  if(robot.brain.get("seen-users") == null){
    robot.brain.set("seen-users", []);
  }
  var users = robot.brain.get("seen-users");
  robot.enter(function(res){
    if(res.message.room != "general")
    var idx = users.findIndex(function(val){return val ===res.message.user.name});
    if (idx === undefined || idx < 0){
      welcomeMessages.forEach(function(msg, i) {
        setTimeout(function(){
          res.send(msg);
        }, messageTime*i);
      });
      users.push(res.message.user.name);
    }
  });
}