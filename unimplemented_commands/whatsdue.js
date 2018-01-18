// Description
//   Prints all assessment for a given list of courses.
//
// Commands:
//   `!whatsdue [COURSE CODE]...` - Prints all assessment for a given list of courses (default: current channel)
//   `!calendar [COURSE CODE]...` - Generates a downloadable calendar containing all assessment for a given list of courses (default: current channel)

var cheerio = require('cheerio');
var ical = require('ical.js');

module.exports = function (robot) {

    // The course and assessment urls to get profile and assessment info.
    var courseUrl = 'https://www.uq.edu.au/study/course.html?course_code=';
    var assessmentUrl = 'https://www.courses.uq.edu.au/student_section_report.php?report=assessment&profileIds=';

    /**
     * Gets the profile id for a course given its course code.
     *
     * @param {string} course code (eg. CSSE2310)
     * @return {!Promise} A promise that resolves with the profile id or an error.
     */
    function getProfileId(course) {
        return new Promise((resolve, reject) => {
            robot.http(courseUrl + course).get() ((err, resp, body) => {
                if (err) {
                    reject('There was an error getting the course profile.');
                    return;
                }

                // Look for first instance of `/profileId=`. Will always point to the latest profile id for the course.
                // If there is no profileId, check to ensure the course code is valid and return the relevant error
                // message.
                var profileID = String(body.match(/profileId=\d*/));
                if (profileID !== 'null') {
                    resolve(profileID.replace('profileId=',''));
                } else if (body.match(/is not a valid course code/) || body.match(/Unable to find course code/)) {
                    reject(course + ' is not a valid course code.');  
                } else {
                    reject(course + ' has no available course profiles.');  
                }
            });
        });
    }

    /**
     * Parses the assessment data provided in the assessment url and returns an array of assessments.
     *
     * @param {string} url linking to the assessment data
     * @return {!Promise} A promise that resolves with an array of assessments or an error.
     */
    function getAssessment(url) {
        return new Promise(resolve => {
            robot.http(url).get() ((err, resp, body) => {
                if (err) {
                    reject('There was an error getting the assessment.');
                    return;
                }

                var $ = cheerio.load(body);
                assessment = [];

                // Look for the tblborder class, which is the assessment data table, then loop over its children
                // starting at index 1 to skip over the column headers (subject, task, due date and weighting).
                //
                // Note: Scraped assessment data is inconsistently formatted and may my assumptions below may make it
                // look ugly. Soz, tell UQ to standardise their shiet.
                $('.tblborder').children().slice(1).each((index, element) => {
                    var columns = $(element).children();

                    var subject = $(columns[0]).find('div').text().slice(0, 8);
                    var task = $(columns[1]).find('div').html().replace(/<br>/g, ' - ').trim();
                    var dueDate = $(columns[2]).find('div').html().split('<br>')[0].trim();
                    var weighting = $(columns[3]).find('div').html().split('<br>')[0].trim();

                    if (!subject || !task || !dueDate || !weighting) {
                        reject('There was an error parsing the assessment.');
                        return;
                    }

                    assessment.push([subject, task, dueDate, weighting]);
                });

                resolve(assessment);
            });
        });
    }

    /**
     * Get a pretty formatted string of all the assessment pieces.
     *
     * @param {Array} array of assessment items
     * @return {string} A formatted string of assessment items
     */
    function getFormattedAssessment(assessment) {
        var formattedAssessment = '_*WARNING:* Assessment information may vary/change/be entirely different! Use at ' +
                                  'your own discretion_\r\n>>>';
                                  
        assessment.map(function(a) {
            formattedAssessment += '*' + a[0] + '*: `' + a[3] + '` _' + a[1] + '_ *(' + a[2] + ')*\r\n';
        })

        return formattedAssessment;
    }

    /**
     * Generate iCal calendar containing the assessment pieces and upload it to slack.
     *
     * @param {Array} array of assessment items
     * @param {channel} the channel that the calendar will be posted to
     * @return {!Promise} A promise that resolves with the importable calendar or an error
     */
    function getCalendar(assessment, channel) {
        var cal = new ical.Component(['vcalendar', [], []]);
        cal.updatePropertyWithValue('prodid', '-//uqcsbot whatsdue assessment generation');
        cal.updatePropertyWithValue('version', '2.0');

        // Loop over assessment and create a calendar event for each one
        assessment.map(function(a) {
            var vevent = new ical.Component('vevent');
            var event = new ical.Event(vevent);
            vevent.updatePropertyWithValue('dtstamp', ICAL.Time.now());
            event.summary = a[0] + ' (' + a[3] + '): ' + a[1].split(' - ')[0];
            event.uid = Math.random().toString();

            // If examination date
            // TODO(mitch): scrape http://www.uq.edu.au/events/calendar_view.php?category_id=16&year=2017 for dates?
            if (a[2] == 'Examination Period') {
                event.startDate = new ical.Time.fromJSDate(new Date('4 November 2017'), false);
                event.endDate = new ical.Time.fromJSDate(new Date('18 November 2017'), false);

            // If normal date
            // Note: Checks year is at least this year to catch cases like 'Tutorial, week 3'
            } else if (Date.parse(a[2]) > Date.parse('1/1/' + new Date().getFullYear())) {
                event.startDate = new ical.Time.fromJSDate(new Date(a[2]), false);

            // If date range
            // TODO(mitch): make this cleaner pls
            } else if (Date.parse(a[2].split('-')[0]) && Date.parse(a[2].split('-')[1])) {
                event.startDate = new ical.Time.fromJSDate(new Date(a[2].split('-')[0]), false);
                event.endDate = new ical.Time.fromJSDate(new Date(a[2].split('-')[1]), false);

            // Else ask person to manually schedule
            } else {
                event.summary = 'WARNING: DATE PARSING FAILED\nPlease manually set date for event!\n' + event.summary
                event.startDate = new ical.Time.now();
            }

            cal.addSubcomponent(vevent);
        });

        // Upload the generated calendar to slack and post it the channel
        return robot.adapter.client.web.files.upload('assessmentCalendar.ics', {
            channels: channel,
            title: 'Importable calendar containing your assessment!',
            file: {
                value: cal.toString(),
                options: {
                    filename: 'assessmentCalendar.ics',
                    contentType: 'text/calendar',
                    knownLength: cal.toString().length
                }
            }
        });
    }

    /**
     * Parses the input string for assessment.
     */
     function parseAssessment(res) {
        var channel = null;
        // Get the channel name (and treat it as a course code!).
        if (robot.adapter.client && robot.adapter.client.rtm) {
            channel = robot.adapter.client.rtm.dataStore.getChannelById(res.message.room);
        }

        // Check there is either a valid channel or a valid input.
        if (!(channel && channel.name) && !res.match[1]) {
            res.send('Please enter at least one valid course.');
            return;
        }

        // If the user has provided a course list, use that; else, use the current channel as the course code.
        var courses = (res.match[1]) ? res.match[1].split(' ') : [channel.name];

        // Create a Promise for each course.
        var profileResponses = [];
        for (var i = 0; i < courses.length; i++) {
            profileResponses.push(getProfileId(courses[i].toUpperCase()));
        }

        // Resolve all the Promises to obtain an array of profile ids. Join them together to create the necessary
        // assessment url to parse and display back to the user.
        return Promise.all(profileResponses)
            .then(profiles => assessmentUrl + profiles.join())
            .then(url => getAssessment(url));
     }

    /**
     * Robot responds to a message containing `!whatsdue`.
     */
    robot.respond(/!?whatsdue ?((?: ?[a-z0-9]+)+)?$/i, function (res) {
        parseAssessment(res)
        .then(assessment => res.send(getFormattedAssessment(assessment)))
        .catch(error => res.send(error));
    });

    /**
     * Robot responds to a message containing `!calendar`.
     */
    robot.respond(/!?calendar ?((?: ?[a-z0-9]+)+)?$/i, function (res) {
        parseAssessment(res)
        .then(assessment => getCalendar(assessment, res.message.room))
        .catch(error => res.send(error));
    });
};
