// Description
//   Better shrug
//
// Commands:
//   !`spider` - Shows spider shrug
//
//
module.exports = function (robot) {
	robot.respond(/!?spider/i, function (res) {
		res.send("//\\; ;/\\\\");
  });
};
