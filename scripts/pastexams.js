// Description
//   Retrives past exams for a subject.
//
// Commands:
//   !`pastexams /[a-z0-9]+/` - Retrieves past exams for a subject
//   !`pastexams` - Retrieves past exams for the current channel
//   !`pastexams ENGG2800` - Shows a list of past exams for ENGG2800
//   !`pastexams ENGG2801` - Prints an error message

var cheerio = require('cheerio');

module.exports = function (robot) {

    /**
     * Gets a list of past exams for a course given its course code.
     *
     * @param {string} course code (eg. CSSE2310)
     * @return {!Promise} A promise that resolves with a list of past exams or an error.
     */
    function getPastExams(course) {
        return new Promise((resolve, reject) => {
            var URL = 'https://www.library.uq.edu.au/exams/papers.php?stub=' + course;

            robot.http(URL).get() ((err, resp, body) => {
                if (err) {
                    reject('There was an error getting the past exams.');
                    return;
                }

                if (body.match(/is not a valid course code/)) {
                    reject(course + ' is not a valid course code.');  
                    return;
                }

                var $ = cheerio.load(body);

                tableRows = $('.maintable').children();
                semesters = tableRows.slice(1).children().slice(1);
                links = tableRows.slice(2).children().slice(1);
                numExams = Math.min(semesters.length, links.length)

                exams = [];
                // Add exam titles
                semesters.slice(0, numExams).each((index, element) => {
                    title = $(element).html().replace(/<br>|\./g, ' ');
                    exams[index] = [title];
                });
                // Add exam link
                links.slice(0, numExams).each((index, element) => {
                    link = $(element).find('a').attr('href');
                    exams[index].push(link);
                });

                resolve(exams);
            });
        });
    }


    /**
     * Get a pretty formatted string of all the exams.
     *
     * @param {Array} array of exam items
     * @return {string} A formatted string of exam items
     */
    function formatExams(examList) {
        var formattedExams = '>>>';
                                  
        examList.map(function(a) {
            formattedExams += '*' + a[0] + '*: <' + a[1] + '|PDF>\r\n';
        });

        return formattedExams;
    }

    /**
     * Robot responds to a message containing `!pastexams`.
     */
    robot.respond(/!?pastexams ?([a-z0-9]+)?$/i, function (res) {
        var channel = null;
        // Get the channel name (and treat it as a course code!).
        if (robot.adapter.client && robot.adapter.client.rtm) {
            channel = robot.adapter.client.rtm.dataStore.getChannelById(res.message.room);
        }

        // Check there is either a valid channel or a valid input.
        if (!(channel && channel.name) && !res.match[1]) {
            res.send('Please enter a valid course.');
            return;
        }

        var course = res.match[1] || channel.name;

        // Get past exams, format them, then print them to the channel
        getPastExams(course.toUpperCase())
            .then(exams => formatExams(exams))
            .then(formatted => res.send(formatted))
            .catch(error => res.send(error));
    });
};
