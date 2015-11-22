// Description
//   Example conversations.
// 
// Commands:
//   !parking - Lists the available parking at UQ
// 


var Conversation = require('hubot-conversation');
module.exports = function (robot) {

    var switchBoard = new Conversation(robot);

    robot.respond(/what is love?/, function (msg) {
        var dialog = switchBoard.startDialog(msg, 5000);
        msg2.reply('Baby don\'t hurt me');
        
        dialog.timeout = function (msg2) {
            msg.reply('C-C-C-C-Combo Breaker!');
        }
        dialog.addChoice(/don't hurt me/i, function (msg2) {
            msg3.reply('no more');
        });
    });

    robot.respond(/jump/, function (msg) {
        var dialog = switchBoard.startDialog(msg);
        msg.reply('Sure, How many times?');

        dialog.addChoice(/([0-9]+)/i, function (msg2) {
            var times = parseInt(msg2.match[1], 10);
            for (var i = 0; i < times; i++) {
                msg.emote("Jumps"); //We can use the original message too.
            }
        });
    });


  robot.respond(/.*the mission/, function (msg) {
        msg.reply('Your have 5 seconds to accept your mission');
        var dialog = switchBoard.startDialog(msg, 5000); //5 Second timeout
        dialog.timeout = function (msg2) {
            msg2.reply('Boom');
        }
        dialog.addChoice(/yes/i, function (msg2) {
            msg2.reply('Great! Here are the details...');
        });
    });
};