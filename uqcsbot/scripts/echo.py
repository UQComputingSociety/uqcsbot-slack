from uqcsbot import command_handler, api

@command_handler.on("echo")
def handle_echo(command):
    if command.has_arg():
        api.post_message(command.channel, command.arg)