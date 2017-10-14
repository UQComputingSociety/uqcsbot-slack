// Description
//   Shutdown uqcsbot
//
// Commands:
//   `!uqcsbot shutdown` - Shuts down uqcsbot, waiting to be restarted via CESI

var admin = ['trm', 'mcdee', 'csa', 'guthers', 'artemis', 'rob', 'mb'];

module.exports = function (robot) {
    robot.respond(/!?uqcsbot shutdown/i, function (res) {
        comandee = res.message.user.name
        if (in_array(comandee, admin)) {
            robot.messageRoom("bot-testing", comandee + " ordered me to shutdown!", "Shutting down.");
            setTimeout(() => robot.shutdown(), 1000);
        } else {
            res.send("YOU CAN'T TELL ME WHAT TO DO!!1");
        }
    });
};

function in_array(str, array) {
    for (var i = 0; i < array.length; i++) {
        if (str.toLowerCase() === array[i].toLowerCase()) {
            return true;
        }
    }
    return false;
}