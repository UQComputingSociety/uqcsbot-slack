// Description
//   Loads purescript
//

module.exports = function(robot){
  try{
    var ps = require('./lib/purescript_main.js');
    ps.setup(robot)();
  } catch (e) {
    console.log(e.message + '\nNOTE: you can generally ignore the above purescript error! :)');
  }
}
