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
	robot.respond(/!?reactify ?([a-zA-Z0-9 ]+)?$/i, function (res) {
		if (robot.adapter.client && robot.adapter.client.rtm) {
			// Adds reaction to the provided item (a message)
			var add_reaction = function(item, emoji, callback) {
				robot.adapter.client.web.reactions.add(emoji,
					{"channel": item.room, "timestamp": item.id},
					callback);
			};

			var item = res.message;
			// Get text, all in lowercase and remove all whitespace
			var msg = res.match[1].toLowerCase().replace(/ /g, "");

			// React in reverse order since it seems reacts occur in
			// first in last out order.
			for (var i = msg.length - 1; i >= 0; i--) {
				// Get random emoji from our dictionary of lists
				var react = emoji[msg[i]][Math.floor(Math.random() * emoji[msg[i]].length)];
				add_reaction(item, react);
			}
        }
  });
};
