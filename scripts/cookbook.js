// Description
//   Returns a link to the UQCS student-compiled cookbook (full of tasty treats).
// Commands
//   `!cookbook` - returns the URL of the UQCS student-compiled cookbook (pdf).
//

module.exports = function (robot) {
  robot.respond(/!?cookbook/i, function (res) {
    res.send("https://jenkins.uqcs.org.au/job/cookbook/lastSuccessfulBuild/artifact/main.pdf");
  });
};
