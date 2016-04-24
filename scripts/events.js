// Description
//   Parses the UQCS calendar (https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics)
//
// Commands:
//   !`events` _<description of time>_ - List UQCS Events
//

var ical = require('ical');
module.exports = function (robot) {
	robot.respond(/!?events ?(full|[1-9][0-9]*)? ?(weeks?)?/i, function (res) {
		var months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
		var no_result = ["There doesn't appear to be any events in the next two weeks...",
				 "There doesn't appear to be any events in the next *<n>* weeks...",
				 "There doesn't appear to be any upcoming events...",
				 "There doesn't appear to be any upcoming events..."];
		var header = ["Events in the *next two weeks*",
			      "Events in the *next _<n>_ weeks*",
			      "The next <n> events",
			      "List of *all* upcoming events"];
		var type = 0; // Two weeks
		if (res.match[1] !== undefined) {
			if (res.match[1] === "full") {
				type = 3; // All events
			} else if (res.match[2] === undefined) {
				type = 2; // n events
			} else {
				type = 1; // n weeks
			}
		}
		ical.fromURL('https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics', {}, function(err, data) {
			var now = new Date().getTime();
			var week = 1000*60*60*24*7;
			var arr = [];
			var n = +res.match[1];
			for(var k in data) {
				if(n === 0) { break; }
				switch(type) {
					case 0:
						if(data[k].end.getTime() > now && data[k].start.getTime() < now + week*2) {
							arr.push(data[k]);
						}
						break;
					case 1:
						if(data[k].end.getTime() > now && data[k].start.getTime() < now + week*n) {
							arr.push(data[k]);
						}
						break;
					case 2:
					case 3:
						if(data[k].end.getTime() > now){
							arr.push(data[k]);
						}
						break;
				}
			}
			arr.sort(function(a,b) { return a.start.getTime()-b.start.getTime(); });

			if(type === 2) {
				arr = arr.slice(0, n);
			}

			var ret = "";
			if(arr.length === 0) {
				ret += "_";
				ret += no_result[type].replace("<n>", res.match[1]);
				ret += "_\r\nFor a full list of events, visit: https://uqcs.org.au/calendar.html\r\n";
			}
			else {
				ret += header[type].replace("<n>", res.match[1]);
				ret += "\r\n";
				for(var k in arr) {
					var ev = arr[k];
					if(ev.location == "") {ev.location = "TBA";}
					ret += "*" + months[ev.start.getMonth()] + " " + ev.start.getDate() + " " + ev.start.getHours() + ":" +
						(ev.start.getMinutes() < 10 ? "0" : "") + ev.start.getMinutes() +
						" - " + months[ev.end.getMonth()] + " " + ev.end.getDate() + " " + ev.end.getHours() + ":" +
						(ev.end.getMinutes() < 10 ? "0" : "") + ev.end.getMinutes() + "*" +
						" - _" + ev.location + "_" +
						": `" + ev.summary + "`\r\n";
				}
			}
			res.send(ret);
		});
	});
}
