module.exports = (robot) ->
  robot.respond /go down/i, (msg) ->
    msg.reply "Restarting"
    process.exit(0)

  robot.router.post "/#{robot.name}/restart", (req, res) ->
    process.exit(0)
