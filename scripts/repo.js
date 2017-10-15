// Description
//   Returns the url for the UQCSbot repo
//
// Commands:
//   `!repo` - Returns the url for the UQCSbot repo

module.exports = function (robot) {
    robot.respond(/!?repo/i, function (res) {
        res.send("https://github.com/UQComputingSociety/uqcsbot");
  });
};
