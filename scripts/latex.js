// Description
//   Converts text wrapped in LaTeX characters to a gif
// Commands
//   $$ \text{LaTeX} $$ - converts text to LaTeX
//

module.exports = function(robot){
  robot.hear(/\$\$([^\$]+)\$\$/, function(res){
    res.send("http://latex.codecogs.com/gif.latex?" + encodeURIComponent(res.match[1]));
  });
};