// Description
//   Allows UQCSbot to pass through the messages it recieves to an unlimited number of endpoints
//   Saving precious Slack integrations
//
// Commands:
//   N/A
//
// Config format:
// [ { "name": passthroughName, "endpoint": URL, patterns: [ regex patterns to listen for ] } ]
//

var request = require("request");


module.exports = function (robot) {

    var passthroughs = [
        {
            "name": "Gricey",
            "endpoint": "http://api.threespark.com/slack/v1/uqcs",
            "patterns": [
                /.*/
            ]
        },
    ];

    passthroughs.forEach(function (passthroughConfig) {
        var name = passthroughConfig.name;
        var endpoint = passthroughConfig.endpoint;
        passthroughConfig.patterns.forEach(function (pattern) {
            robot.hear(pattern, function (res) {
                var envelope = res.envelope;
                request.post(endpoint, {
                    form: {
                        "channel_name": envelope.room,
                        "user_id": envelope.user,
                        "user_name": envelope.user_name,
                        "text": envelope.message.text,
                    }
                });
            });
        });
    });

};
