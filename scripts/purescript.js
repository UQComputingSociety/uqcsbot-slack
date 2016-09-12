module.exports = function(robot){
  try{
    var ps = require('./lib/purescript_main.js');
    ps.scripts(robot)();
  } catch (e) {
    console.log("Error loading purescript lib");
  }
}
