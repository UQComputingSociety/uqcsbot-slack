// Description
//   Parses the UQCS calendar (https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics)
//
// Commands:
//   `!events [full|all|NUM EVENTS|<NUM WEEKS> weeks]` - List UQCS Events
//

var ical = require('ical');
module.exports = function (robot) {
	robot.respond(/!?events ?(full|all|[1-9][0-9]*)? ?(weeks?)?/i, function (res) {
		var months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
		var now = new Date().getTime();
		var week = 1000*60*60*24*7;

		var to = null; // Time until, false values imply no end
		var cap = 0; // Maximum number of events, 0 implies no cap

		var no_result_msg = "Looks like there aren't any ";
		var header;

		if (res.match[1] === undefined) {
			// Two weeks
			to = now + week * 2;
			no_result_msg += "events in the next two weeks...";
			header = "Events in the *next two weeks*";
		} else if (res.match[1] !== "full" && res.match[1] !== "all") {
			var n = +res.match[1]; // Convert to num
			if (res.match[2] === undefined) {
				cap = n; // n events
				no_result_msg += "upcoming events...";
				header = "The *next _" + n + "_ events*";
			} else {
				to = now + week * n; // n weeks
				no_result_msg += "events in the next *" + n + "* weeks...";
				header = "Events in the *next _n_ weeks*";
			}
		} else {
			// All
			no_result_msg += "upcoming events...";
			header = "List of *all* upcoming events";
		}

		ical.fromURL('https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics', {}, function(err, data) {
			var arr = [];
			for(var k in data) {
				if(n === 0) { break; }
				if(data[k].type == 'VTIMEZONE') { continue; } // I don't even know. See issue #50 on peterbraden/ical.js
				if(data[k].rrule) {
					// Repeated event, stored in the format from the rrule package
					var times; // List of repeated times in the desired time-frame
					if(to) {
						times = data[k].rrule.between(new Date(now), new Date(to));
					} else {
						// Technically until a year ahead, safer this way.
						times = data[k].rrule.between(new Date(now), new Date(now + week * 52));
					}
					var obj;
					var duration = data[k].end.getTime() - data[k].start.getTime(); // How long it goes for
					for(var i = 0; i < times.length; i++) {
						obj = {};
						// Copy necessary information from the original event
						obj.location = data[k].location;
						obj.summary = data[k].summary;
						// Set new start/end
						obj.start = times[i];
						obj.end = new Date(times[i].getTime() + duration);

						arr.push(obj);
					}
				} else if(data[k].end.getTime() > now) {
					if(!to || data[k].start.getTime() < to) {
						arr.push(data[k]);
					}
				}
			}
			arr.sort(function(a, b) {
				return a.start.getTime() - b.start.getTime();
			});

			if(cap) {
				arr = arr.slice(0, cap);
			}

			var ret = "";
			if(arr.length === 0) {
				ret += "_" + no_result_msg + "_\r\nFor a full list of events, visit: https://uqcs.org.au/calendar.html\r\n";
			}
			else {
				ret += header + "\r\n";
				for(var k in arr) {
					var ev = arr[k];
					if(ev.location == "") { ev.location = "TBA"; }

					var start_time = months[ev.start.getMonth()] + " " + ev.start.getDate() + " " + ev.start.getHours() + ":" +
						(ev.start.getMinutes() < 10 ? "0" : "") + ev.start.getMinutes();

					var end_time = ev.end.getHours() + ":" + (ev.end.getMinutes() < 10 ? "0" : "") + ev.end.getMinutes();
					if (ev.start.getMonth() !== ev.end.getMonth() || ev.start.getDate() !== ev.end.getDate()) {
						end_time = months[ev.end.getMonth()] + " " + ev.end.getDate() + " " + end_time;
					}

					ret += "*" + start_time + " - " + end_time + "*" +
						" - _" + ev.location + "_" +
						": `" + ev.summary + "`\r\n";
				}
			}
			res.send(ret);
		});
	});
}
