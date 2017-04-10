// Description
//   Spells out words with emoji
//
// Commands:
//   !`reactify` _<word>_ - Spells out the given word with emoji!

// Dictionary of characters mapping to emojis.
var emoji = {
	'a': ["a", "adobe", "airbnb", "alpha", "anarchism", "arch"],
	'b': ["b", "beta", "bitcoin"],
	'c': ["c", "cpp", "cygwin"],
	'd': ["d", "disney"],
	'e': ["e", "ecorp", "emacs", "erlang"],
	'f': ["f"],
	'g': ["g"],
	'h': ["h", "haskell"],
	'i': ["i"],
	'j': ["js"], // Closest J I could find
	'k': ["k"],
	'l': ["l"], // Closest L I could find
	'm': ["maccas"],
	'n': ["n"],
	'o': ["palantir", "tf2"],
	'p': ["p", "producthunt"],
	'q': ["q"],
	'r': ["r", "registered", "redroom"],
	's': ["s", "stanford", "sublime"],
	't': ["t"],
	'u': ["u"],
	'v': ["v", "vim"],
	'w': ["w"],
	'x': ['xbox'],
	'y': ["y"],
	'z': ["zoidberg"], // No Z?

	'1': ["one"],
	'2': ["two"],
	'3': ["three"],
	'4': ["four"],
	'5': ["five"],
	'6': ["six"],
	'7': ["seven"],
	'8': ["eight"],
	'9': ["nine"],
	'0': ["zero"]
};

module.exports = function (robot) {
	robot.respond(/!?reactify ?(.+)?$/i, function (res) {
		if (robot.adapter.client && robot.adapter.client.rtm) {
			// Adds reaction to the provided item (a message)
			var add_reaction = function(item, emoji, callback) {
				robot.adapter.client.web.reactions.add(emoji,
					{"channel": item.room, "timestamp": item.id},
					callback);
			};

			var item = res.message;
			// Get text, all in lowercase and remove non alphanumeric
			var msg = res.match[1].toLowerCase().replace(/[^a-zA-Z0-9]/g, "");

			// React in reverse order since it seems reacts occur in
			// first in last out order.
      var used_reacts = [];
			for (var i = msg.length - 1; i >= 0; i--) {
				// Get random emoji from our dictionary of lists
        var possible_reacts = emoji[msg[i]].filter(x => used_reacts.indexOf(x) < 0);
        if (possible_reacts.length < 1) {
          continue;
        }
				var react = possible_reacts[Math.floor(Math.random() * possible_reacts.length)];
				add_reaction(item, react);
        used_reacts.push(react);
			}
    }
  });
};
