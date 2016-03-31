// Description
//   Parses the UQCS calendar (https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics)
//
// Commands:
//   !events - List UQCS Events
//

var ical = require('ical');
module.exports = function (robot) {
	robot.respond(/!?events ?(full|[1-9][0-9]*)? ?(weeks?)?/i, function (res) {
		var months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
		if (res.match[1] === undefined) { res.match[1] = ""; }
		if (res.match[2] === undefined) { res.match[2] = ""; }
		ical.fromURL('https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics', {}, function(err, data) {
			var now = new Date().getTime();
			var week = 1000*60*60*24*7;
			var arr = [];
			// !events
			if (res.match[1] === ""){
				for(var k in data) {
					// Hasn't finished, and it starts in at least two weeks
					if(data[k].end.getTime() > now && data[k].start.getTime() < now + week*2) {
						arr.push(data[k]);
					}
				}
			// !events full
			} else if (res.match[1] === "full"){
				for(var k in data){
					if(data[k].end.getTime() > now){
						arr.push(data[k]);
					}
				}
			// !events <n> weeks
			} else if (res.match[2] !== "") {
				var n = +res.match[1];
				for(var k in data) {
					if(data[k].end.getTime() > now && data[k].start.getTime() < now + week*n) {
						arr.push(data[k]);
					}
				}
			// !events <n>
			} else {
				var n = +res.match[1];
				for(var k in data) {
					if(n === 0) { break; }
					arr.push(data[k]);
					n--;
				}
			}
			var ret = "";
			if(arr.length === 0) {
				if (res.match[1] === "") {
					ret += "_There doesn't appear to be any events in the next two weeks..._\r\n";
				} else if (res.match[2] !== "") {
					ret += "_There doesn't appear to be any events in the next *" + res.match[1] + "* weeks..._\r\n";
				} else {
					ret += "_There doesn't appear to be any upcoming events..._\r\n";
				}
				ret += "For a full list of events, visit: https://uqcs.org.au/calendar.html\r\n";
			}
			else {
				arr.sort(function(a,b) { return a.start.getTime()-b.start.getTime(); });
				if(res.match[1] === ""){
					ret += "Events in the *next two weeks*. For a list of all events, visit: https://uqcs.org.au/calendar.html\r\n";
				} else if (res.match[2] !== "") {
					ret += "Events in the *next _" + res.match[1] + "_ week" + (res.match[1] !== "1" ? "s" : "") + "*. For a list of all events, visit: https://uqcs.org.au/calendar.html\r\n";
				} else if (res.match[1] !== "full"){
					ret += "The next " + res.match[1] +" events. For a list of all events, visit: https://uqcs.org.au/calendar.html\r\n";
				} else {
					ret += "List of all upcoming events. For a list of events (including previous ones), visit: https://uqcs.org.ay/calendar.html\r\n";
				}
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
