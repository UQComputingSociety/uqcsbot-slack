// Description
//   Voteythumbs, uses thumb up or down emojis to vote
//
// Commands:
//   !`voteythumbs <message> - Shows your slack user id
//
//
module.exports = function (robot) {
	var reset_brain = function() {
		robot.brain.set("voteythumbs", {votes:{}});
	};
	var get_id = function(channel, ts, user) {
		return channel + "-" + ts + "-" + user;
	};
	var check_if_passed = function(id) {
		var votes = robot.brain.get("voteythumbs");
		if(votes === null) {
			reset_brain();
			votes = robot.brain.get("voteythumbs");
			if(votes === null) { return; }
		}
		//Get channel count
		var channel_id = id.split("-")[0];
		var channel = robot.adapter.client.getChannelGroupOrDMByID(channel_id);
		if(channel.members === undefined) {
			//DM
			var active = 1;
		}else {
			var active = channel.members.filter(function(user) {
				var slack = robot.brain.userForId(user).slack;
				return slack.deleted === false && slack.is_bot === false;
			}).length;
		}
		var to_pass = active / 2;
		if(votes.votes[id].count > to_pass) {
			//Passed
			robot.messageRoom(channel_id, "Vote: " + votes.votes[id].text + ". Passed\r\n");
			votes.votes[id] = undefined;
		}else if(votes.votes[id].count < -to_pass) {
			//Failed
			robot.messageRoom(channel_id, "Vote: " + votes.votes[id].text + ". Failed\r\n");
			votes.votes[id] = undefined;
		}
	};
	var voteythumbs_message = function(res) {
		var votes = robot.brain.get("voteythumbs");
		if(votes === null) {
			reset_brain();
			votes = robot.brain.get("voteythumbs");
			if(votes === null) { return; }
		}

		var item = res.message.rawMessage;
		votes.votes[get_id(item.channel, item.ts, item.user)] = {count: 0, text: res.match[1]};

		var add_reaction = function(item, emoji, callback) {
			robot.http("https://slack.com/api/reactions.add?token="
					+ process.env.HUBOT_SLACK_TOKEN
					+ "&name=" + emoji
					+ "&channel=" + item.channel
					+ "&timestamp=" + item.ts).get() (
						function(err, resp, body) {
							if(resp.error) {
								console.log("Adding reaction failed: " + resp.error);
							}
							if(callback) { callback(); }
						});
		};
		add_reaction(item, "thumbsup", function() {
			add_reaction(item, "thumbsdown");
		});
	};
	robot.respond(/!?voteythumbs:? (.+)/, function (res) {
		voteythumbs_message(res);
	});
	robot.hear(/@channel voteythumbs:? (.+)/, function(res) {
		voteythumbs_message(res);
	});
	robot.adapter.client.on("raw_message", function(message) {
		var votes = robot.brain.get("voteythumbs");
		if(votes === null) {
			reset_brain();
			votes = robot.brain.get("voteythumbs");
			if(votes === null) { return; }
		}
		if(message.type === "reaction_added") {
			if(robot.brain.userForId(message.user).slack.is_bot) { return; }
			var item = message.item;
			var emoji = 0;
			var id = get_id(item.channel, item.ts, message.item_user);
			if(votes.votes[id] === undefined) { return; }

			if(message.reaction === "+1") { emoji = 1; }
			if(message.reaction === "-1") { emoji = -1; }

			votes.votes[id].count += emoji;
			check_if_passed(id);
		}else if(message.type === "reaction_removed") {
			if(robot.brain.userForId(message.user).slack.is_bot) { return; }
			var item = message.item;
			var emoji = 0;
			var id = get_id(item.channel, item.ts, message.item_user);
			if(votes.votes[id] === undefined) { return; }

			if(message.reaction === "+1") { emoji = 1; }
			if(message.reaction === "-1") { emoji = -1; }

			votes.votes[id].count -= emoji;
			check_if_passed(id);
		}
	});

};
