// Description
//   We need a shrug to go with spider
//
// Commands:
//   !`shrug` - Shows normal shrug
//   ¯\_(ツ)_/¯
//
module.exports = function (robot) {
	robot.respond(/!?shrug/i, function (res) {
		res.send("¯\\_(ツ)_/¯");
  });
};
