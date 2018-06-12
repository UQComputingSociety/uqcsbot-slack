// Description
//   Allows UQCSBot to participate in werewolf
//
// Commands:
//   `!werewolf` - When used in #werewolf, UQCSBot will play
//

module.exports = function (robot) {
	// !werewolf
	robot.respond(/!?werewolf/i, function (res) {
		if(res.room === "werewolf") {
			// Join
			res.send("!join");
			// Clear memory
			robot.brain.set('werewolf_ai', {});
		}
	});

	// Setting role
	robot.respond(/Your role is (.+)/, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		ai.role = res.match[1];
	});

	// Get list of players
	robot.hear(/Remaining Players: (.+)+/, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		var alive = res.match[1].split(", ");
		// This will be run on night 1 to get the players
		if(ai.players === undefined) {
			ai.players = {}
			for(var i = 0; i < alive.length; i++) {
				ai.players[alive[i]] = {
					role: "",
					accusations: {}
				};
			}
			res.send("!vote noone");
		}else {
			// Check if we know somebody is a werewolf
			var werewolf = "";
			for(var i = 0; i < alive.length; i++) {
				var name = ai.players[alive[i]].role.toLowerCase();
				if(name === "werewolf") {
					werewolf = name;
					break;
				}
			}
			if(werewolf !== "") {
				res.send("!vote " + werewolf);
			}else {
				// Don't know any werewolves
				// 10% chance of being a bully
				if(Math.random() < 0.1) {
					// Random lynch
					res.send("!vote " + alive[Math.floor(Math.random() * alive.length)]);
				}else {
					res.send("!vote noone");
				}
			}
		}
	});

	// Somebody died
	robot.hear(/With pitchforks in hand, the townsfolk killed: (.+) \((.+)\)/, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		var name = res.match[1];
		// If they were seer, take their accusations as fact
		if(res.match[2] === "Seer") {
			var facts = ai.players[name].accusations;
			var keys = keys(facts);
			for(var i = 0; i < keys.length; i++) {
				ai.players[keys[i]].role = facts[keys[i]];
			}
		}
		delete ai.players[name];
	});

	// If I'm the seer...
	robot.hear(/if i('| a)m (the|a) seer,? i saw (.+) as ?a? (.+)/i, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		ai.players["@" + res.user.name].accusations[res.match[1]] = res.match[2];
	});

	// Select person to killed
	robot.respond(/It is night and it is time to hunt/, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		var players = keys(ai.players);
		setTimeout(function() {
			res.send("!kill #werewolf " + players[Math.floor(Math.random() * players.length)]);
		}, Math.random() * 3000 + 2000);
	});

	// Seer select
	robot.respond(/Seer, select a player/, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		var unknown = [];
		var players = keys(ai.players);
		for(var i = 0; i < players; i++) {
			if(ai.players[players[i]].role === "") {
				unknown.push(ai.players[players[i]]);
			}
		}

		if(unknown.length === 0) {
			unknown.push(players[Math.floor(Math.random() * players.length)]);
		}

		setTimeout(function() {
			res.send("!see #werewolf " + unknown[Math.floor(Math.random() * unknown.length)]);
		}, Math.random() * 3000 + 2000);
	});

	// Seer results
	robot.respond(/(.+) is on the side of the (.+)/, function(res) {
		var ai = robot.brain.get('werewolf_ai');
		ai.players[res.match[1]] = res.match[2];
	});
}
