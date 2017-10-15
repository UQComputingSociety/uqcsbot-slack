// Description
//   Shell for UQCSBot (allows advanced use of commands)
//
// Commands:
//   `!exec <COMMAND>` - Executes the shell command

module.exports = function (robot) {
	function run_cmd(res, cmd) {
		// Allow lack of starting '!'
		if(cmd[0] != '!') {
			cmd = "!" + cmd;
		}

		var output = "";
		// When the command is run, it will execute this when it calls res.send
		var fake_send = function(str) {
			output += str;
		};

		var found = false; // Found a command?
		for(var i = 0; i < robot.listeners.length; i++) {
			if(robot.listeners[i].regex == undefined) {
				continue;
			}

			// Check the command
			var matches = robot.listeners[i].regex.exec(cmd);
			if(matches != null) {
				found = true;
				// Call the command's function with a fake `res`
				var new_res = new robot.Response(robot, res.message, matches);
				new_res.send = fake_send;
				robot.listeners[i].callback(new_res);
			}
		}

		if(!found) {
			output = "Invalid command: '" + cmd + "'.\n";
		} else if(output.length == 0) {
			output = "No output.\n";
		}

		return output;
	}

	function tokenize(cmd) {
		var tokenized = [];
		var cur = ""; // Current token
		var open = 0; // # Of open brackets
		for(var i = 0; i < cmd.length; i++) {
			// '!('
			if(cmd[i] == '(' && cur.length > 0 && cur[cur.length - 1] == '!') {
				cur = cur.slice(0, cur.length - 1); // Remove the '!' from cur token
				if(cur.length > 0) {
					tokenized.push(cur);
					cur = "";
				}
				tokenized.push("!(");
				open++;
			} else if(cmd[i] == ')' && open > 0) {
				if(cur.length > 0) {
					tokenized.push(cur);
					cur = "";
				}
				tokenized.push(")");
				open--;
			 } else {
				 cur += cmd[i];
			 }
		}

		if(cur.length > 0) {
			tokenized.push(cur);
		}
		return tokenized;
	}

	function substitute_vals(res, tokens) {
		if(tokens.length == 1) {
			return tokens[0];
		}
		for(var i = 0; i < tokens.length; i++) {
			if(tokens[i] == "!(" && i < tokens.length - 1) {
				// Possibly a command substitution, find closing bracket
				var count = 0; // Current bracket 'level'
				var closing = -1; // Index of closing bracket
				for(var j = i + 1; j < tokens.length; j++) {
					if(tokens[j] == "!(") { count++; }
					if(tokens[j] == ")") {
						if(count == 0) {
							closing = j;
							break;
						} else {
							count--;
						}
					}
				}
				// No closing bracket, not a valid command sub, ignore
				if(closing == -1) {
					continue;
				}
				// Recursive
				var subbed = substitute_vals(res, tokens.slice(i + 1, j));
				subbed = run_cmd(res, subbed); // Evaluate
				tokens.splice(i, j - i + 1, subbed); // Substitute

				// Flatten
				if(i > 0) {
					if(tokens[i - 1] != "!(" && tokens[i - 1] != ")") {
						tokens[i - 1] += tokens[i];
						tokens.splice(i, 1);
					}
				}
				if(i < tokens.length - 1) {
					if(tokens[i + 1] != ")" && tokens[i + 1] != "!(") {
						tokens[i] += tokens[i + 1];
						tokens.splice(i + 1, 1);
					}
				}

				i--; // Recheck this token
			}
		}
		return tokens;
	}

	robot.respond(/!?exec (.+)/i, function (res) {
		var message = res.match[1];
		var tokens = tokenize(message);
		var evald = substitute_vals(res, tokens);
		res.send(evald.join("") + '\n');
	});
}
