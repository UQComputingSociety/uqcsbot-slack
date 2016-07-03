// Description
//   Generates help commands for Hubot.
//
// Commands:
//   !`parking` - Lists the available parking at UQ
//

var safeEval = require("safe-eval");

module.exports = function (robot) {
	robot.respond(/!?javascript ?(.+)?/i, function (res) {
        var code = res.match[1] || "('==' == '===' && '==' === '===')";

        var evaluated = "You sneaky bastard! I ain't running: \r\n";
        evaluated += "```\r\n" + code + "\r\n```";

        try {
            evaluated = safeEval(code);
        } catch (e) {
            // They did a bad thing!
        }

        res.send("```\r\n" + code + "\r\n```\r\n" + "evaluates to:" + "\r\n```\r\n" + evaluated + "\r\n```");
	});
}
