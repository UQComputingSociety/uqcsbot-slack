// Description
//   Welcomes new users to UQCS Slack
//

var welcomeMessages = [
	"Hey there! Welcome to the UQCS slack!",
	"This is the first time I've seen you, so you're probably new here",
	"I'm UQCSbot, your friendly (open source) robot helper",
	"Introduce yourself on #intros, join some channels",
	"We've got a bunch of generic channels (e.g. #banter, #games, #projects) along with some subject-specific ones",
	"Your friendly admins are @trm, @svict4, @gricey, @rachcatch, @ainsleynand, @dmarj97",
	"Type \"help\" here, or \"uqcsbot help\" anywhere else to find out what I can do.",
	"and again, welcome :)"
];

// NUMBER OF PEOPLE: MESSAGE
var unique_messages = {
	400: "Bad Request",
	401: "Unauthorized",
	402: "Payment Required",
	403: "Forbidden",
	404: "Not Found",
	405: "Method Not Allowed",
	406: "Not Acceptable",
	407: "Proxy Authentication Required",
	408: "Request Timeout",
	409: "Conflict",
	410: "Gone",
	411: "Length Required",
	412: "Precondition Failed",
	413: "Payload Too Large",
	414: "URI Too Long",
	415: "Unsupported Media Type",
	416: "Range Not Satisfiable",
	417: "Expectation Failed",
	418: "I'm a teapot",
	421: "Misdirected Request",
	422: "Unprocessable Entity",
	423: "Locked",
	424: "Failed Dependency",
	426: "Upgrade Required",
	428: "Precondition Required",
	429: "Too Many Requests",
	431: "Request Header Fields Too Large",
	451: "Unavailable For Legal Reasons"
};

//The time between each individual welcome message send
var messageTime = 2500;

module.exports = function(robot){
	robot.enter(function(res){
		if(res.message.room == "general"){
			members = robot.adapter.client.getChannelGroupOrDMByName("general").members.length;
			res.send("Welcome, " + res.message.user.name + "!");
			var unique = unique_messages[members];
			if(unique !== undefined) {
				setTimeout(function() {
					res.send(members + ": " + unique);
				}, messageTime);
			}

			if(members % 50 == 0) {
				setTimeout(function() {
					res.send(":tada: " + members + " members! :tada:");
				}, messageTime);
			}
			welcomeMessages.forEach(function(msg, i) {
				setTimeout(function(){
					robot.send({room: res.message.user.name}, msg);
				}, messageTime*i);
			});
		}
	});
}
