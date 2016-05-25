// Better shrug

module.exports = function (spiderShrug) {
	robot.respond(/!?spider/i, function (res) {
	  res.send("//\; ;/\\");
  });
};
