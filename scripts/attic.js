// Description
//   Retrieves files from a course's UQAttic folder
//
// Commands:
//   `!attic [COURSE CODE]` - Retrieves UQAttic files for a given course code (default: current channel)

BASE_FOLDER_URL = 'https://drive.google.com/drive/folders/';
BASE_FILE_URL = 'https://drive.google.com/file/d/';
BASE_API_URL = 'https://www.googleapis.com/drive/v3/';
BASE_ATTIC_FOLDER = '0B6_D4T6LJ-uwZmFhMzIyNGYtNTM2OS00ZDJlLTg0NmYtY2IyNzA1MDZlNDIx';
API_KEY = process.env.GOOGLE_API_KEY;
ROOM_FILE_LIMIT = 15; // Number of files allowed to be posted in room, else sent via direct message

// Retrieves all the files from the given folder and all sub-folders
function getAllFiles(robot, folder) {
    return getFolderFiles(robot, folder).then(files => {
        return Promise.all(files.map(file => {
            if (file.mimeType == 'application/vnd.google-apps.folder') {
                return getAllFiles(robot, file);
            } else {
                return Promise.resolve(file);
            }
        }));
    });
}

// Retrives all the files from the given folder
function getFolderFiles(robot, folder) {
    return new Promise((resolve, reject) => {
        folderRequest = BASE_API_URL + `files?q='` + folder.id + `' in parents&key=` + API_KEY;
        robot.http(folderRequest).get()((err, resp, body) => {
            if (err) {
                reject(`There was an error getting the folder '${folder.name}'s contents`);
                return;
            }
            resolve(JSON.parse(body).files);
        });
    });
}

// Flattens the given n-dimensional array down to a one dimensional array
function flattenArray(array) {
    return array.reduce((a,b) => a.concat(Array.isArray(b) ? flattenArray(b) : b), []);
}

module.exports = function (robot) {
	robot.respond(/!?attic ?(.*)/i, function (res) {
        // Make sure we have access to all the clients we need
        if (!robot.adapter.client || !robot.adapter.client.rtm) {
            return;
        }

        // If no course code is provided, use the current channel as default
        var courseCode = res.match[1];
        if (!courseCode) {
            // If the current channel is not in the datastore (e.g. is likely a DM), return the correct usage and exit
            var channel = robot.adapter.client.rtm.dataStore.getChannelById(res.message.room);
            if (!channel) {
                res.send('> Usage: `!attic [COURSE CODE]`');
                return;
            }

            courseCode = channel.name;
        }
        courseCode = courseCode.toUpperCase();

        // Retrieve base UQAttic folder
        var baseFolderRequest = BASE_API_URL + `files?q='` + BASE_ATTIC_FOLDER +
                                `' in parents and mimeType = 'application/vnd.google-apps.folder'&key=` + API_KEY;
        robot.http(baseFolderRequest).get() ((err, resp, body) => {
            if (err) {
                res.send('There was an error getting the base UQAttic folder');
                return;
            }

            // Retrieve the user specified course folder
            var courseFolder = JSON.parse(body).files.find(course => course.name.toUpperCase() == courseCode);
            if (!courseFolder) {
                res.send(`No course folder found for ${courseCode}`);
                return;
            }

            // Send the course folder link to the channel, then attempt to retrieve all files from the course folder 
            var msg = `Retrieving all files from <${BASE_FOLDER_URL}${courseFolder.id}|UQAttic's ${courseCode} Folder>...`;
            robot.send({room: res.message.room}, msg)[0].then(() => {
                getAllFiles(robot, courseFolder).then(files => {
                    // Flatten and format files
                    var flatFiles = flattenArray(files);
                    var formattedFiles = flatFiles.map(file => `> *${file.name}*: <${BASE_FILE_URL}${file.id}|Link>`);

                    // If there is too many files, send directly to user, else send to channel
                    if (formattedFiles.length > ROOM_FILE_LIMIT) {
                        user = res.message.user;
                        name = user.profile.display_name || user.name;
                        res.send(`Too many files to display, sent results directly to ${name}`);
                        robot.send({room: user.id}, formattedFiles.join('\n'));
                    } else {
                        res.send(formattedFiles.join('\n'));
                    }
                }).catch(err => console.log(err));
            });
        });
    });
};