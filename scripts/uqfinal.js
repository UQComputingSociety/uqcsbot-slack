// Description
//   UQFinal: Returns the minimum mark as percentage on the final exam to pass (doesn't include hurdles)
//
// Commands:
//   `!uqfinal <COURSE CODE> <MARK>...` - Returns minimum mark needed on final exam given a course code and a list of assessment marks
//

var math = require("mathjs");

module.exports = function (robot) {
  robot.respond(/!?uqfinal ([a-z]{4}[0-9]{4}[a-z]?) (.+)+/i, function (res) {
    //res.match[1] is the course code
    //res.match[2] is the space-seperated scores
    var semester;
    robot.http("https://api.uqfinal.com/semesters")
      .get()(function (err, resp, body) {
        if (err) {
          res.send("Error: " + err);
          return;
        }

        if (resp.statusCode != 200) {
          res.send("Failure fetching current semester (HTTP Error: " + resp.statusCode + ")");
          return;
        }

        var semesters = JSON.parse(body).data.semesters;
        for (var i = 0; i < semesters.length; i++) {
          if (semesters[i].isCurrent) {
            semester = semesters[i].uqId;
            break;
          } else {
          }
        }

        if (!semester) {
          res.send("Error: Cannot find the current semester.");
          return;
        }

        robot.http("https://api.uqfinal.com/course/" + semester + "/" + res.match[1])
          .get()(function (err, resp, body) {
            if (err) {
              res.send("Error: " + err);
              return;
            }

            if (resp.statusCode != 200) {
              res.send("Invalid Course (Error " + resp.statusCode + ")");
              return;
            }

            var course = JSON.parse(body).data;
            var num_of_assessment = course.assessment.length;
            var scores = res.match[2].split(" ");

            if (scores.length != num_of_assessment - 1) {
              res.send("Invalid number of arguments. Course has " + num_of_assessment + " pieces of assessment, you gave " + scores.length + ".\nKeep in mind you need to leave the last piece of assessment out.");
              return;
            }

            var total = 0;
            var invalid = false;
            for (var i = 0; i < num_of_assessment - 1; i++) {

              try {
                var evaluated = math.eval(scores[i]);
              } catch (err) {
                res.send("Invalid score: " + scores[i] + ". Reason: Unparsable");
                invalid = true;
                break;
              }

              if (evaluated > 0 && evaluated < 1) {
                res.send("_Note: Treating '" + scores[i] + "' (" + evaluated + ") as: " + evaluated * 100 + "%_");
                evaluated *= 100;
              }

              if (evaluated < 0 || evaluated > 100) {
                res.send("Invalid score: " + scores[i] + ". Reason: Score is not within 0 and 100");
                invalid = true;
                break;
              }

              total += (evaluated / 100) * course.assessment[i].weight;

            }

            if (!invalid) {
              var needed = 50 - total;
              var result = Math.ceil(needed / course.assessment[num_of_assessment - 1].weight * 100);
              res.send("You need to achieve at least " + result + "% on the final exam.\n_Disclaimer: this does not take hurdles into account_\n_Powered by http://uqfinal.com_");
            }
          });
      });
  });
};
