// Description
//   Shutdown uqcsbot
//
// Commands:
//   `!shutdown` - Shuts down uqcsbot, waiting to be restarted via CESI

module.exports = function (robot) {
    robot.respond(/!?shutdown/i, function (res) {
        comandee = res.message.user
        if (comandee.is_admin) {
            robot.messageRoom("bot-testing", comandee.name + " ordered me to shutdown!", "Shutting down.");
            setTimeout(() => robot.shutdown(), 1000);
        } else {
            res.send("YOU CAN'T TELL ME WHAT TO DO!!1");
        }
    });
};