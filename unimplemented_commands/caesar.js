// Description
//   Performs Caesar shift on specified text
//
// Commands:
//   `!caesar[n] <TEXT>` - Performs Caesar shift on text (default: 47)

module.exports = function (robot) {
	robot.respond(/!?caesar(\-?\d*) (.+)/i, function (res) {
		var n = 0;
		if(res.match[1] == "") { n = 47; }
        else { n = Number(res.match[1]); }
		caesar = "";
		var c = 0;
		for(var i = 0; i < res.match[2].length; i++) {
			// 32 (SPACE) to 126 (~)
			// Get ascii code - 32. This makes SPACE the equivalent of 0
			// + n. Add caesar shift
			// mod 94 (from 126-32=94). This prevents overflow
			// + 32. Changes back (so SPACE is back to 32 instead of 0)
			c = res.match[2].charCodeAt(i)
			c -= 32;
			c += n;
            c = ((c % 94) + 94) % 94;
			c += 32;
			caesar += String.fromCharCode(c);
		}
		res.send(caesar);
	});
}
