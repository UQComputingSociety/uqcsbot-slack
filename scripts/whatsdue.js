// Description
//   Prints all assessment for a given array of courses.
//
// Commands:
//   !`whatsdue`` _<course1>_ _<course2>_ ... - Prints all assessment for a
//                                              given array of courses.

var cheerio = require('cheerio');

module.exports = function (robot) {

    // The course and assessment urls to get profile and assessment info.
    var courseUrl = 'https://www.uq.edu.au/study/course.html?course_code=';
    var assessmentUrl = 'https://www.courses.uq.edu.au/student_section_report' +
                        '.php?report=assessment&profileIds=';

    /**
     * Gets the profile id for a course given its course code.
     *
     * @param {string} course code (eg. CSSE2310)
     * @return {!Promise} A promise that resolves with the profile id
     *                    or an error.
     */
    function getProfileId(course) {
        return new Promise((resolve, reject) => {
            robot.http(courseUrl + course).get() ((err, resp, body) => {
                if (err) {
                    reject('There was an error getting the course profile.');
                    return;
                }

                // Look for first instance of `/profileId=`. Will always point
                // to the latest profile id for the course.
                var profileID = String(body.match(/profileId=\d*/));
                if (profileID !== 'null') {
                    resolve(profileID.replace('profileId=',''));
                } else {
                    reject(course + ' is not a valid course code.');
                }
            });
        });
    }

    /**
     * Parses the assessment data provided in the assessment url and returns
     * an array of assessments.
     *
     * @param {string} url linking to the assessment data
     * @return {!Promise} A promise that resolves with an array of assessments
     *                    or an error.
     */
    function parseAssessmentData(url) {
        return new Promise(resolve => {
            robot.http(url).get() ((err, resp, body) => {
                if (err) {
                    reject('There was an error getting the assessment.');
                    return;
                }

                var $ = cheerio.load(body);
                var assessment = '_*WARNING:* Assessment information may ' +
                                 'vary/change/be entirely different! Use ' +
                                 'at your own discretion_\r\n>>>';

                // Look for the tblborder class, which is the assessment data
                // table, then loop over its children starting at index 1 to
                // skip over the column headers (subject, task, due date and
                // weighting).
                // TODO(mitch): make this less ugly and bleh.
                // Note: Formatting of assessment data is inconsistent and may
                //       look ugly. Soz.
                $('.tblborder').children().slice(1).each((index, element) => {
                    var columns = $(element).children();

                    var subject = $(columns[0]).find('div')
                                  .text().trim().slice(0, 8);
                    var task = $(columns[1]).find('div')
                               .html().trim().replace('<br>', ' - ');
                    var dueDate = $(columns[2]).find('div')
                                  .text().trim();
                    var weighting = $(columns[3]).find('div')
                                    .text().trim();

                    if (!subject || !task || !dueDate || !weighting) {
                        reject('There was an error parsing the assessment.');
                        return;
                    }

                    assessment += '*' + subject + '*: ' +
                                  '`' + task + '` ' +
                                  '_(' + dueDate + ')_ ' +
                                  '*' + weighting + '*\r\n';
                });

                resolve(assessment);
            });
        });
    }

    /**
     * Robot responds to a message containing `!whatsdue`.
     */
    robot.respond(/!?whatsdue ?((?: ?[a-z]{4}[0-9]{4})+)?$/i, function (res) {
        var channel = null;
        // Get the channel name (and treat it as a course code!).
        if (robot.adapter.client && robot.adapter.client.rtm) {
            channel = robot.adapter.client.rtm.dataStore
                      .getChannelById(res.message.room).name;
        }

        // Prevent local testing failing (when robot.adapter.client is null)
        if (!channel && !res.match[1]) {
            res.send('Please enter at least one course to test.');
            return;
        }

        // If the user has provided a course list, use that; else, use the
        // current channel as the course code.
        var courses = (res.match[1]) ? res.match[1].split(' ') : [channel];

        // Create a Promise for each course.
        var profileResponses = [];
        for (var i = 0; i < courses.length; i++) {
            profileResponses.push(getProfileId(courses[i]));
        }

        // Resolve all the Promises to obtain an array of profile ids. Join
        // them together to create the necessary assessment url to parse and
        // display back to the user. Print any errors that occured.
        Promise.all(profileResponses)
            .then(profiles => assessmentUrl + profiles.join())
            .then(url => parseAssessmentData(url))
            .then(assessment => res.send(assessment))
            .catch(error => res.send(error));
    });
};