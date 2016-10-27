// Description
//   Shell for UQCSBot (allows advanced use of commands)
//
// Commands:
//   !`shell` _<command>_ - Executes the shell command
//
module.exports = function (robot) {
	function run_cmd(res, cmd) {
		if(cmd[0] != '!') {
			cmd = "!" + cmd;
		}
		var output = "";
		var fake_send = function(str) {
			output += str;
		};
		var found = false;
		for(var i = 0; i < robot.listeners.length; i++) {
			if(robot.listeners[i].regex == undefined) {
				continue;
			}
			var matches = robot.listeners[i].regex.exec(cmd);
			if(matches != null) {
				found = true;
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

	function substitute_vals(res, cmd) {
		var matches = /!\((.+?)\)/.exec(cmd);
		var new_cmd = cmd;
		if(matches == null) {
			return cmd;
		}
		for(var i = 1; i < matches.length; i++) {
			var subbed = substitute_vals(res, matches[i]);
			var evald = run_cmd(res, subbed);
			new_cmd = new_cmd.replace("!(" + matches[i] + ")", evald);
		}
		return new_cmd;
	}

	robot.respond(/!?exec (.+)/i, function (res) {
		var message = res.match[1];
		var evald = substitute_vals(res, message);
		res.send(evald + '\n');
	});
}
