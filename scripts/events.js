// Description
//   Parses the UQCS calender (https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics)
// 
// Commands:
//   !events - List UQCS Events
//

var ical = require('ical');
module.exports = function (robot) {
	robot.hear(/^!events$/i, function (res) {
		var months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
		ical.fromURL('https://calendar.google.com/calendar/ical/q3n3pce86072n9knt3pt65fhio%40group.calendar.google.com/public/basic.ics', {}, function(err, data) {
			var now = new Date().getTime();
			for(var k in data) {
				var ev = data[k];
				if(ev.end.getTime() > now) {
					res.send("*" + months[ev.start.getMonth()] + " " + ev.start.getDate() +"*" +
						" - _" + ev.location + "_" +
						": `" + ev.summary + "`");
				}
			}
		});
	});
}
