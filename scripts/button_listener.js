// Description
//   Listens for button post requests
//

const YES_VOTE = 0;
const NO_VOTE = 1;
const ABSTAIN_VOTE = 2;

module.exports = function (robot) {
    robot.router.post("/button", function(req, res) {
        var payload = JSON.parse(req.body.payload);
        //robot.logger.info(payload);
        // Verification token
        if (payload.token == process.env.SLACK_VERIFICATION_TOKEN) {
            res.end(); // Return response early to reduce timeouts
            if (payload.callback_id == 'vote') {              
                if (payload.actions[0].name == 'yes') {
                    process_vote(payload, res, YES_VOTE);
                }
                else if (payload.actions[0].name == 'no') {
                    process_vote(payload, res, NO_VOTE);
                }
                else {
                    // Unknown action
                }
            }
        }
        else {
            res.writeHead(403, {'Content-Type': 'text/plain'});
            res.end();
        }
    });


    function process_vote(payload, res, type) {
        var attachments = payload.original_message.attachments;

        // Add voter to appropriate field
        var newVoteList = attachments[0].fields[type].value
         + "\r" + payload.user.name;
        attachments[0].fields[type].value = newVoteList;

        // Increment vote counter
        var title = attachments[0].fields[type].title;
        var count = parseInt(title[title.length - 2]) + 1;
        robot.logger.info(count);
        
        if (type == YES_VOTE) {
            attachments[0].fields[type].title = "Yes (" + count + ")";
        }
        else if (type == NO_VOTE) {
            attachments[0].fields[type].title = "No (" + count + ")";
        }
        else {

        }

        robot.logger.info(attachments[0].fields[type]);

        // Update message
        robot.adapter.client.web.chat.update(payload.message_ts,
            payload.channel.id, payload.original_message.text,
            {"attachments": attachments, "link_names": false});
    }
};
