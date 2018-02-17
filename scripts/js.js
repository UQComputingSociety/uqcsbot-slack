// Description
//   Runs and evaluates snippets of JavaScript
//
// Commands:
//   `!js <JAVASCRIPT CODE>` - Returns the (safe) evaluation of the given JavaScript

const safeEval = require("safe-eval");

module.exports = function (robot) {
	robot.respond(/!?(javascript|js) ?(.+)?/i, function (res) {
        const code = res.match[2] || "('==' == '===' && '==' === '===')";
        let responseLines;

        try {
            const result = safeEval(code);
            responseLines = [
                "```",
                code,
                "```",
                "evaluates to:",
                "```",
                result,
                "```"
            ];
        } catch (e) {
            // They did a bad thing!
            responseLines = [
                "You sneaky bastard! I ain't running:",
                "```",
                code,
                "```"
            ];
        }

        res.send(responseLines.join("\r\n"));
	});
}
