// Description
//   Parses the UQCS calendar (https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics)
//
// Commands:
//   !events - List UQCS Events
//

var ical = require('ical');
module.exports = function (robot) {
	robot.respond(/!?events/i, function (res) {
		var months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
		ical.fromURL('https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics', {}, function(err, data) {
			var now = new Date().getTime();
			var arr = [];
			for(var k in data) {
				// Hasn't finished, and it starts in at least two weeks
				if(data[k].end.getTime() > now && data[k].start.getTime() < now + 1000*60*60*24*14) {
					arr.push(data[k]);
				}
			}
			var ret = "";
			if(arr.length == 0) {
				ret = "_There doesn't appear to be any events in the next two weeks..._\r\n";
				ret += "For a full list of events, visit: https://uqcs.org.au/calendar.html\r\n";
			}
			else {
				arr.sort(function(a,b) { return a.start.getTime()-b.start.getTime(); });
				ret = "Events in the *next two weeks*. For a list of all events, visit: https://uqcs.org.au/calendar.html\r\n";
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
