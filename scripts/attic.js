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

function getAllFiles(robot, folderId) {
    folderRequest = BASE_API_URL + `files?q='` + folderId + `' in parents&key=` + API_KEY;
    return new Promise((resolve, reject) => {
        robot.http(folderRequest).get()((err, resp, body) => {
            if (err) {
                reject('There was an error getting the course folder');
                return;
            }

            var folderFiles = [];
            JSON.parse(body).files.forEach(file => {
                if (file.mimeType == 'application/vnd.google-apps.folder') {
                    console.log(file.name);
                    getAllFiles(robot, file.id).then(subFiles => {
                        folderFiles.push(...subFiles);
                    });
                } else {
                    folderFiles.push(`*${file.name}*: <${BASE_FILE_URL}${file.id}|Link>`);
                }
            });

            resolve(folderFiles);
        });
    });
}

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

            getAllFiles(robot, courseFolder.id).then(result => res.send('>>>' + result.join('\n')));
        });
  });
};