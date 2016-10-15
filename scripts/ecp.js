// Description
//   Finds links for electronic course profiles.
//
// Commands:
//   !`ecp /[a-zA-Z]{4}\d{4}/` - Finds the link to the ECP for the given course profile
//   !`ecp ENGG2800` - Shows the electronic course profile of ENGG2800
//   !`ecp ENGG2801` - Prints an error message
module.exports = function (robot) {
    robot.respond(/!?ecp [a-zA-Z]{4}\d{4}/, function (res) {
        var match = res.match[0];
        var course = match.split(" ")[1];
        var URL = "https://www.uq.edu.au/study/course.html?course_code=" + course;
        robot.http(URL).get() (function(err, resp, body) {
            var profileID = String(body.match(/profileId=\d*/));
            if (profileID === "null") {
                res.send(["Course \"", course, "\" does not exist."].join(""));
            } else {
                var link = "www.courses.uq.edu.au/student_section_loader.php?section=1&";
                res.send(["The ECP of \"", course, "\" is located at ", link.concat(profileID)].join(""));
            }
        });
    });
};
