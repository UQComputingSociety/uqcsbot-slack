// Description
//   TODO
//
// Commands:
//   TODO

BASE_FOLDER_URL = 'https://drive.google.com/drive/folders/'
BASE_FILE_URL = 'https://drive.google.com/file/d/'
BASE_API_URL = 'https://www.googleapis.com/drive/v3/'

BASE_ATTIC_FOLDER_ID = '0B6_D4T6LJ-uwZmFhMzIyNGYtNTM2OS00ZDJlLTg0NmYtY2IyNzA1MDZlNDIx'
API_KEY = 'AIzaSyD6JDGpJMv-tPh-vOJB-MLr9_cqskdGmGA'

module.exports = function (robot) {
	robot.respond(/!?attic ?(.*)/i, function (res) {
        var courseCode = res.match[1];
        if (!courseCode) {
            res.send(BASE_FOLDER_URL + BASE_ATTIC_FOLDER_ID);
            return;
        }
        courseCode = courseCode.toUpperCase();

        var baseFolderRequest = BASE_API_URL + `files?q='` + BASE_ATTIC_FOLDER_ID + `' in parents and mimeType = 'application/vnd.google-apps.folder'&key=` + API_KEY;
        robot.http(baseFolderRequest).get() ((err, resp, body) => {
            if (err) {
                res.send('There was an error getting the base folder');
                return;
            }

            var courseFolder = JSON.parse(body).files.find(course => course.name.toUpperCase() == courseCode);
            if (!courseFolder) {
                res.send(`No course folder found for ${courseCode}`);
                return;
            }

            courseFolderRequest = BASE_API_URL + `files?q='` + courseFolder.id + `' in parents&key=` + API_KEY;
            robot.http(courseFolderRequest).get() ((err, resp, body) => {
                if (err) {
                    console.log('There was an error getting the course folder');
                    return;
                }

                courseFiles = JSON.parse(body).files.map(file => `*${file.name}*: <${BASE_FILE_URL}${file.id}|Link>`);
                res.send('>>>' + courseFiles.join('\n'));
            });

        });
  });
};