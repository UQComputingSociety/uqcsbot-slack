// Description
//   Prints all assessment for a given array of courses.
//
// Commands:
//   !`whatsdue`` _<course1>_ _<course2>_ ... - Prints all assessment for a given array of courses.

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
                // TODO(mitch): make this less ugly and bleh.
                //
                // Note: Scraped assessment data is inconsistently formatted and may my assumptions below may make it
                // look ugly. Soz, tell UQ to standardise their shiet.
                $('.tblborder').children().slice(1).each((index, element) => {
                    var columns = $(element).children();

                    var subject = $(columns[0]).find('div').text().slice(0, 8);
                    var task = $(columns[1]).find('div').html().replace('<br>', ' - ').trim();
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
     * Loop over each assessment and concatentate the subject, task, due date and weighting in nice formatting.
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
     * Generate iCal calendar containing the assessment pieces and return a link to it.
     */
    function getCalendar(assessment, userChannel) {
        //
        var cal = new ical.Component(['vcalendar', [], []]);
        cal.updatePropertyWithValue('prodid', '-//uqcsbot whatsdue assessment generation');
        cal.updatePropertyWithValue('version', '2.0');

        //
        assessment.map(function(a) {
            var vevent = new ical.Component('vevent');
            vevent.updatePropertyWithValue('dtstamp', ICAL.Time.now());

            var event = new ical.Event(vevent);
            event.summary = a[0] + ' (' + a[3] + '): ' + a[1].split(' - ')[0];
            event.uid = Math.random().toString();


            // If examination date
            // TODO(mitch): scrape http://www.uq.edu.au/events/calendar_view.php?category_id=16&year=2017 for dates
            if (a[2] == 'Examination Period') {
                event.startDate = new ical.Time.fromJSDate(new Date('4 November 2017'), false);
                event.endDate = new ical.Time.fromJSDate(new Date('18 November 2017'), false);
                console.log(1);

            // if normal date
            } else if (Date.parse(a[2])) {
                event.startDate = new ical.Time.fromJSDate(new Date(a[2]), false);
                console.log(2);

            // if date range
            } else if (Date.parse(a[2].split('-')[0]) && Date.parse(a[2].split('-')[1])) {
                event.startDate = new ical.Time.fromJSDate(new Date(a[2].split('-')[0]), false);
                event.endDate = new ical.Time.fromJSDate(new Date(a[2].split('-')[1]), false);
                console.log(3);

            // else ask person to manually schedule
            //TODO(mitch): ensure strings like 'Tutorial, week 3' and '10am Mon week 5, Tues week 10 & Mon week 13' are caught
            } else {
                event.summary = 'WARNING: Date of assessment could not be parsed, please manually set date for event!\n' + event.summary
                event.startDate = new ical.Time.now();
                console.log(4);
            }

            console.log(event.startDate.toString() + ' ' + a[2]);

            // time = Date.parse(a[3])/1000;
            // console.log(time);
            // console.log(new ical.Time.fromUnixTime(time));

            cal.addSubcomponent(vevent);
        });

        // TODO(mitch): add calendar toggle for command
        
        // 
        return robot.adapter.client.web.files.upload('assessmentCalendar.ics', {
            channels: userChannel,
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
     * Robot responds to a message containing `!whatsdue`.
     */
    robot.respond(/!?whatsdue ?((?: ?[a-z0-9]+)+)?$/i, function (res) {
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
        // assessment url to parse and display back to the user. Print any errors that occured.
        Promise.all(profileResponses)
            .then(profiles => assessmentUrl + profiles.join())
            .then(url => getAssessment(url))
            .then(assessment => {
                res.send(getFormattedAssessment(assessment));
                return getCalendar(assessment, res.message.user.id);
            })
            .catch(error => res.send(error));
    });
};