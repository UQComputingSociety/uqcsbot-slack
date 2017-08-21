// Description
//   Gets the Bureau of Meteorology's latest radar image
// Commands
//   !`radar` - Gets Brisbane's radar
//

module.exports = function (robot) {
  robot.respond(/!?radar/i, function (res) {
    res.send("https://bom.lambda.tools/?location=brisbane&_cache=" + Date.now());
  });
};
