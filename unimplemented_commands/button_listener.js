// Description
//   Listens for button post requests
//

const YES_VOTE = 0;
const NO_VOTE = 1;
const CLEAR_VOTE = 2;

module.exports = function (robot) {
    robot.router.post("/button", function(req, res) {
        var payload = JSON.parse(req.body.payload);
        // Verification token
        if (payload.token == process.env.SLACK_VERIFICATION_TOKEN) {
            res.end(); // Return response early to reduce timeouts
            if (payload.callback_id == 'vote') {              
                if (payload.actions[0].name == 'yes') {
                    process_action(payload, res, YES_VOTE);
                }
                else if (payload.actions[0].name == 'no') {
                    process_action(payload, res, NO_VOTE);
                }
                else if (payload.actions[0].name == 'clear') {
                    process_action(payload, res, CLEAR_VOTE);
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


    function process_action(payload, res, type) {
        if (type == YES_VOTE) {
            process_vote(payload, res, type);
        }
        else if (type == NO_VOTE) {
            process_vote(payload, res, type);
        }
        else if (type == CLEAR_VOTE) {
            // Remove our user from the vote list if they're on it
            remove_vote(payload, YES_VOTE);
            remove_vote(payload, NO_VOTE);
        }

        // Update vote count
        var attachments = payload.original_message.attachments;
        attachments[0].fields[YES_VOTE].title = "Yes (" + count_votes(payload, YES_VOTE) + ")";
        attachments[0].fields[NO_VOTE].title = "No (" + count_votes(payload, NO_VOTE) + ")";

        // Update message
        robot.adapter.client.web.chat.update(payload.message_ts,
            payload.channel.id, payload.original_message.text,
            {"attachments": payload.original_message.attachments});
    }

    function process_vote(payload, res, type) {
        var attachments = payload.original_message.attachments;
        var voteList = attachments[0].fields[type].value;
        var name = payload.user.name;
        var title = attachments[0].fields[type].title;

        // Check if our user has voted already
        if (voteList.search("\n" + name) == -1) {
            // Add voter to appropriate field
            var newVoteList = voteList + "\n" + name;
            attachments[0].fields[type].value = newVoteList;
        }

        // Remove vote from other list if it exists
        if (type == YES_VOTE) {
            remove_vote(payload, NO_VOTE);
        }
        else {
            remove_vote(payload, YES_VOTE);
        }
    }

    function remove_vote(payload, type) {
        var attachments = payload.original_message.attachments;
        var name = payload.user.name;
        var voteList = attachments[0].fields[type].value;
        attachments[0].fields[type].value = voteList.replace("\n" + name, "");
    }

    function count_votes(payload, type) {
        // This seems like a bad way to store vote info (and count it)
        var count = 0;
        var list = payload.original_message.attachments[0].fields[type].value;
        for (var i = 0; i < list.length; i++) {
            if (list[i] === '\n') {
                count++;
            }
        }
        return count;
    }
};
