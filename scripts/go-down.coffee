# Description:
#   Restarts uqcsbot
#
# Commands:
#   *uqcsbot* `go down` - Shuts down uqcsbot, waiting to be restarted via CESI
#
# URLS:
#   /hubot/restart

module.exports = (robot) ->
  robot.respond /go down/i, (msg) ->
    msg.reply "Restart command recieved"
    robot.logger.info "#{msg.message.user.name} sent restart command"
    robot.messageRoom "bot-testing", "<@#{msg.message.user.name}> has shut me down. Don't worry, I auto-restart."
    process.exit(1)

  robot.router.post "/#{robot.name}/restart", (req, res) ->
    process.exit(1)
