// Description
//   Allows users to vote yes/no to a question
//
// Commands:
//   !`vote` <name> - Start's a vote with the given name
//

module.exports = function (robot) {
    robot.respond(/!?vote ?(.+)/i, function (res) {
        robot.adapter.client.web.chat.postMessage(res.message.room,
            res.message.user.name + ": " + res.match[1],  {
            "attachments": [
                {
                    "text": "",
                    "fallback": "Fail",
                    "color": "#3AA3E3",
                    "callback_id": "vote",
                    "attachment_type": "default",
                    "fields" : [
                        {
                            "title": "Yes (0)",
                            "value": "",
                            "short": true
                        },
                        {
                            "title": "No (0)",
                            "value": "",
                            "short": true
                        },
                    ],
                    "actions": [
                        {
                            "name": "yes",
                            "text": "Yes",
                            "type": "button"
                        },
                        {
                            "name": "no",
                            "text": "No",
                            "type": "button"
                        },
                    ]
                }
            ]}
        );
    });
};
