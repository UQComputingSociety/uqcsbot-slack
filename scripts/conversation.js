// Description
//   Enables two-way conversations
//


var Conversation = require('hubot-conversation');
module.exports = function (robot) {

    var switchBoard = new Conversation(robot);

    robot.respond(/what is love?/, function (msg) {
        var dialog = switchBoard.startDialog(msg);
        msg.reply('Baby don\'t hurt me');

        dialog.timeout = function (msg2) {
            msg2.reply('C-C-C-C-Combo Breaker!');
        }
        dialog.addChoice(/don't hurt me/i, function (msg3) {
            msg3.reply('no more');
        });
    });
};
