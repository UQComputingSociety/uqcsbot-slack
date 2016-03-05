// Description
//   UQFinal
// 
// Commands:
//   uqcsbot <uqfinal|wdinotf|final> <score1> <score2> ... - (scores are the percentages) Returns the minimum mark on the final exam to pass (doesn't include hurdles)
// 

module.exports = function (robot) {
	robot.respond(/(uqfinal|wdinotf|final) ([a-z]{4}[0-9]{4}[a-z]?) (.+)+/i, function (res) {
		//res.match[2] is the course code
		//res.match[3] is the space-seperated scores
		var uqf = robot.http("http://uqfinal.com/json/" + res.match[2].toUpperCase() + ".json")
				.get() (function(err, resp, body) {
					if(err) {
						res.send("Error: " + err);
					}else if(resp.statusCode != 200) {
						res.send("Invalid Course (Error " + resp.statusCode + ")");
					}else {
						var course = JSON.parse(body);
						var num_of_assessment = course.assessment.length;
						var scores = res.match[3].split(" ");
						if(scores.length != num_of_assessment - 1) {
							res.send("Invalid number of arguments. Course has " + num_of_assessment + " pieces of assessment, you gave " + scores.length + ". Keep in mind you need to leave the last piece of assessment out.");
						}else {
							var total = 0;
							var invalid = false;
							for(var i = 0; i < num_of_assessment - 1; i++) {
								if(isNaN(Number(scores[i]))) {
									res.send("Invalid score: '" + scores[i] + "'.");
									invalid = true;
									break;
								}
								total += (scores[i]/100) * course.assessment[i].weight;
							}
							if(!invalid) {
								var needed = 50 - total;
								var result = Math.ceil(needed/course.assessment[num_of_assessment - 1].weight * 100);
								res.send("You need to achieve at least " + result + "% on the final exam. _Disclaimer: this does not take hurdles into account_");
							}
						}
					}
				});
	});
}
