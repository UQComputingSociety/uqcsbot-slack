// Description
//   A script that runs cronjobs for messages or other functions
//

var HubotCron = require('hubot-cronjob');

module.exports = function(robot) {
  var fn, pattern, timezone;
  pattern = '0 0 1 1 *'; // 0 0 1 1 *
  timezone = 'Australia/Brisbane';

  fn = function() {
    return robot.messageRoom("general", "Happy New Year @everyone! :fireworks::confetti_ball::beers:");
  };
  return new HubotCron(pattern, timezone, fn);
};
