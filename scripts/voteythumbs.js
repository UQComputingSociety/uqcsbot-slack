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
		var channel = robot.adapter.client.dataStore.getChannelByName(channel_id);

		if(channel.members === undefined) {
			//DM
			var active = 1;
		} else {
			var active = channel.members.filter(function(user) {
				var slack = robot.brain.userForId(user).slack;
				return slack.deleted === false && slack.is_bot === false;
			}).length;
		}

		var to_pass = active / 2;

		if(votes.votes[id].ups > to_pass) {
			//Passed
			robot.messageRoom(channel_id, ":white_check_mark: Voteythumbs '" + votes.votes[id].text + "'. Passed :white_check_mark:\r\n");
			votes.votes[id] = undefined;
		} else if(votes.votes[id].downs > to_pass) {
			//Failed
			robot.messageRoom(channel_id, ":x: Voteythumbs  '" + votes.votes[id].text + "'. Failed :x:\r\n");
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

		var item = res.message;
		votes.votes[get_id(item.room, item.id, item.user)] = {ups: 0, downs: 0, text: res.match[1]};

		var add_reaction = function(item, emoji, callback) {
			robot.adapter.client.web.reactions.add(emoji,
				{"channel": item.room, "timestamp": item.id},
				callback);
		};

		add_reaction(item, "thumbsup", function(){
			add_reaction(item, "thumbsdown");
		});
	};

	robot.respond(/!?voteythumbs:? (.+)/, function (res) {
		voteythumbs_message(res);
	});

	robot.hear(/@channel:? !?voteythumbs:? (.+)/, function(res) {
		voteythumbs_message(res);
	});

	if(robot.adapter.client && robot.adapter.client.rtm) {
		robot.adapter.client.rtm.on("reaction_added", function(message){
			var votes = robot.brain.get("voteythumbs");

			if(votes === null) {
				reset_brain();
				votes = robot.brain.get("voteythumbs");
				if(votes === null) { return; }
			}

			if(robot.brain.userForId(message.user).is_bot) { return; }

			var item = message.item;
			var id = get_id(item.channel, item.ts, message.item_user);

			if(votes.votes[id] === undefined) { return; }

			if(message.reaction === "+1") {
				votes.votes[id].ups += 1;
			} else if(message.reaction === "-1") {
				votes.votes[id].downs += 1;
			}

			check_if_passed(id);

		});
		robot.adapter.client.rtm.on("reaction_remvoed", function(message){
			var votes = robot.brain.get("voteythumbs");

			if(votes === null) {
				reset_brain();
				votes = robot.brain.get("voteythumbs");
				if(votes === null) { return; }
			}

			if(robot.brain.userForId(message.user).is_bot) { return; }

			var item = message.item;
			var id = get_id(item.channel, item.ts, message.item_user);

			if(votes.votes[id] === undefined) { return; }

			if(message.reaction === "+1") {
				votes.votes[id].ups -= 1;
			} else if(message.reaction === "-1") {
				votes.votes[id].downs -= 1;
			}

			check_if_passed(id);
		});
	}
};
