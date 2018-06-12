# Play naughts and crosses!
from uqcsbot import bot, Command
from uqcsbot.util.attachments_util import *

@bot.on_command("crosses")
def handle_crosses(command: Command):
    '''
    `!crosses` - Plays a game of naughts and crosses
    '''

    # Create the grid ass rows of button attachments
    Atts = Attachments_Util()

    
    for i in range(3):
        Att = Attachment("","")
        btnArray = []
        for j in range(3):
            btnArray.append(LinkButtonAction("-"))
            btnArray[j].action_name = f"{i},{j}"
            btnArray[j].action_value = f"{i},{j}"
        Att.attachment_actions = btnArray
        Atts.add_attachment(Att)

    if Atts.validate() == False:
        bot.logger.error("Fucked up?")

    bot.logger.error(bot.post_message_with_attachments(command.channel, "Lets play naughts and crosses!", Atts))