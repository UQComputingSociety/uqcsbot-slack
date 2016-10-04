module.exports = function(robot){
  try{
    var ps = require('./lib/purescript_main.js');
    ps.setup(robot)();
  } catch (e) {
    console.error(e);
  }
}
