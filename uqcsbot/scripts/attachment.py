from uqcsbot import bot, Command
from uqcsbot.util.attachments_util import *
import json


@bot.on_command("button")
def handle_button(command: Command):
    '''
    `!button` - Shows the test button.
    '''
    Att1 = Attachment("Fallback1","attachement text 1")
    # Att1.attachment_color = AttachmentColor.COLOUR_GOOD
    Att1.attachment_title = "Some title text!"
    Att1.attachment_title_link = "https://github.com/UQComputingSociety/uqcsbot/issues/311"
    Att1.attachment_footer = "Small footer?"
    # Att1.attachment_color = "danger" # American spelling required

    Att2 = Attachment("Fallback2","attachement text 2")
    
    lb = LinkButtonAction("Btn?","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
    Att2.attachment_actions = [lb]

    # Att2.attachment_color = AttachmentColor.COLOUR_DANGER

    Att3 = Attachment("Fallback3","attachement text 3")
    Att3.set_color(AttachmentColor.COLOUR_WARNING)
    # bot.logger.error(Att3.attachment_color)

    Atts = Attachments_Util()
    Atts.add_attachment(Att1)
    Atts.add_attachment(Att2)
    Atts.add_attachment(Att3)

    if Atts.validate() == False:
        bot.logger.error("Fucked up?")

    bot.post_message(command.channel, "message text",  attachments=Atts.toJSON())