// Description
//   Runs and evaluates snippets of JavaScript
//
// Commands:
//   `!js <JAVASCRIPT CODE>` - Returns the (safe) evaluation of the given JavaScript

var safeEval = require("safe-eval");

module.exports = function (robot) {
	robot.respond(/!?(javascript|js) ?(.+)?/i, function (res) {
        var code = res.match[2] || "('==' == '===' && '==' === '===')";

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
