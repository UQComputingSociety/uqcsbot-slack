// Description
//   TODO
//
// Commands:
//   TODO

BASE_FOLDER_URL = 'https://drive.google.com/drive/folders/'
BASE_FILE_URL = 'https://drive.google.com/file/d/'
BASE_API_URL = 'https://www.googleapis.com/drive/v3/'
BASE_ATTIC_FOLDER = '0B6_D4T6LJ-uwZmFhMzIyNGYtNTM2OS00ZDJlLTg0NmYtY2IyNzA1MDZlNDIx'
API_KEY = 'AIzaSyD6JDGpJMv-tPh-vOJB-MLr9_cqskdGmGA'
ROOM_FILE_LIMIT = 15; // Number of files allowed to be posted in room, else sent via direct message

function getAllFiles(robot, folderId) {
    return getFolderFiles(robot, folderId).then(files => {
        return Promise.all(files.map(file => {
            if (file.mimeType == 'application/vnd.google-apps.folder') {
                return getAllFiles(robot, file.id);
            } else {
                return Promise.resolve(file);
            }
        }));
    });
}

function getFolderFiles(robot, folderId) {
    folderRequest = BASE_API_URL + `files?q='` + folderId + `' in parents&key=` + API_KEY;
    return new Promise((resolve, reject) => {
        robot.http(folderRequest).get()((err, resp, body) => {
            if (err) {
                reject('There was an error getting the course folder');
                return;
            }
            resolve(JSON.parse(body).files);
        });
    });
}

function flattenArray(array) {
    return array.reduce((a,b) => a.concat(Array.isArray(b) ? flattenArray(b) : b), []);
}

module.exports = function (robot) {
	robot.respond(/!?attic ?(.*)/i, function (res) {
        var courseCode = res.match[1];
        if (!courseCode) {
            res.send(BASE_FOLDER_URL + BASE_ATTIC_FOLDER);
            return;
        }
        courseCode = courseCode.toUpperCase();

        var baseFolderRequest = BASE_API_URL + `files?q='` + BASE_ATTIC_FOLDER +
                                `' in parents and mimeType = 'application/vnd.google-apps.folder'&key=` + API_KEY;
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

            getAllFiles(robot, courseFolder.id).then(files => {
                var flatFiles = flattenArray(files);
                var formattedFiles = flatFiles.map(file => `> *${file.name}*: <${BASE_FILE_URL}${file.id}|Link>`);
                if (formattedFiles.length > ROOM_FILE_LIMIT) {
                    user = res.message.user;
                    res.send(`Too many files to display, sent results directly to ${user.name}`);
                    robot.send({room: user.id}, formattedFiles.join('\n'));
                } else {
                    res.send(formattedFiles.join('\n'));
                }
            }).catch(err => console.log(err));
        });
  });
};