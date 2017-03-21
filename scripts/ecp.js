// Description
//   Finds links for electronic course profiles.
//
// Commands:
//   !`ecp /[a-z]{4}[0-9]{4}/` - Finds the link to the ECP for the given course profile
//   !`ecp ENGG2800` - Shows the electronic course profile of ENGG2800
//   !`ecp ENGG2801` - Prints an error message
module.exports = function (robot) {

    function getEcp(course, onComplete) {
        var URL = 'https://www.uq.edu.au/study/course.html?course_code=' + course;

        robot.http(URL).get() (function(err, resp, body) {
            if (err) {
                reject('There was an error getting the course profile.');
                return;
            }

            // Look for first instance of `/profileId=`. Will always point
            // to the latest profile id for the course. If there is no
            // profileId, check to ensure the course code is valid and return
            // the relevant error message.
            var profileID = String(body.match(/profileId=\d*/));
            if (profileID !== 'null') {
                var link = 'www.courses.uq.edu.au/student_section_loader.php?' +
                           'section=1&' + profileID;
                onComplete('>*' + course + ' ECP*: ' + link);
            } else if (body.match(/is not a valid course code/)) {
                onComplete(course + ' is not a valid course code.');  
            } else {
                onComplete(course + ' has no available course profiles.');  
            }
        });
    }

    // respond to !`ecp` or !`ecp ENGG2800`
    robot.respond(/!?ecp ?([a-z0-9]+)?$/i, function (res) {
        var channel = null;
        // Get the channel name (and treat it as a course code!).
        if (robot.adapter.client && robot.adapter.client.rtm) {
            channel = robot.adapter.client.rtm.dataStore
                      .getChannelById(res.message.room);
        }

        // Check there is either a valid channel or a valid input.
        if (!(channel && channel.name) && !res.match[1]) {
            res.send('Please enter at least one valid course.');
            return;
        }

        // If the user has provided a course list, use that; else, use the
        // current channel as the course code.
        var course = res.match[1] || channel.name;
        getEcp(course.toUpperCase(), ecp => { res.send(ecp) });
    });
};
