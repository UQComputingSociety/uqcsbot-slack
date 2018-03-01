// Description
//   Moss cat command
//   Why that wasn't there already I don't even know
//
// Commands:
//   `!cat` - Shows the moss cat, brings torture to 2310 students

module.exports = function (robot) {
	robot.respond(/!?cat/i, function (res) {
		res.send("```\n" +
                "         __..--''``\\--....___   _..,_\n" +
                "     _.-'    .-/\";  `        ``<._  ``-+'~=.\n" +
                " _.-' _..--.'_    \\                    `(^) )\n" +
                "((..-'    (< _     ;_..__               ; `'   fL\n" +
                "           `-._,_)'      ``--...____..-'\n```");
  });
};
