// Description
//   Finds links for electronic course profiles.
//
// Commands:
//   !`ecp /[a-z]{4}[0-9]{4}/` - Finds the link to the ECP for the given course profile
//   !`ecp ENGG2800` - Shows the electronic course profile of ENGG2800
//   !`ecp ENGG2801` - Prints an error message
module.exports = function (robot) {

    function getEcp(course, onComplete) {
        var URL = "https://www.uq.edu.au/study/course.html?course_code=" + course;

        robot.http(URL).get() (function(err, resp, body) {
            if (err) {
                reject('There was an error getting the course profile.');
                return;
            }

            var profileID = String(body.match(/profileId=\d*/));
            if (profileID === "null") {
                onComplete("Course '" + course + "' does not exist.");
                return;
            }

            var link = "www.courses.uq.edu.au/student_section_loader.php?section=1&" + profileID;
            onComplete("The ECP of '" + course + "' is located at " + link);
        });
    }

    // respond to !`ecp` or !`ecp ENGG2800`
    robot.respond(/!?ecp ?([a-z]{4}[0-9]{4})?$/i, function (res) {
        var course = res.match[1] || res.message.room;
        getEcp(course, ecp => { res.send(ecp) });
    });
};
