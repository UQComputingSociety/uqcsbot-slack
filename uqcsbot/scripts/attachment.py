from uqcsbot import bot, Command
from uqcsbot.util.attachments_util import *
import json


@bot.on_command("button")
def handle_button(command: Command):
    '''
    `!button` - Shows the test button.
    '''
    Att1 = Attachment("Fallback1","attachement text 1")
    Att1.attachment_title = "Some title text!"
    Att1.attachment_title_link = "https://github.com/UQComputingSociety/uqcsbot/issues/311"
    Att1.attachment_footer = "Small footer?"
    Att1.set_color(AttachmentColor.COLOUR_GOOD)

    Att2 = Attachment("Fallback2","attachement text 2")
    lb1 = LinkButtonAction("Btn1","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
    lb2 = LinkButtonAction("Btn2","https://github.com/UQComputingSociety/uqcsbot/issues/311", ButtonStyle.STYLE_DANGER)
    lb3 = LinkButtonAction("Btn3","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
    lb4 = LinkButtonAction("Btn4","https://github.com/UQComputingSociety/uqcsbot/issues/311", ButtonStyle.STYLE_DANGER)
    lb5 = LinkButtonAction("Btn5","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
    Att2.attachment_actions = [lb1,lb2,lb3,lb4,lb5]
    Att2.set_color(AttachmentColor.COLOUR_DANGER)

    Att3 = Attachment("Fallback3","attachement text 3")
    Att3.set_color(AttachmentColor.COLOUR_WARNING)
    Att3.attachment_pretext = "pretext for attachment 3 looks like normal text, sort of..."
    f1 = AttachmentField("Title 1","foo",False)
    f2 = AttachmentField("Title 2","bar",True)
    f3 = AttachmentField("Title 3","baz",True)
    Att3.attachment_fields = [f1, f2, f3]

    Atts = Attachments_Util()
    Atts.add_attachment(Att1)
    Atts.add_attachment(Att2)
    Atts.add_attachment(Att3)

    if Atts.validate() == False:
        bot.logger.error("Fucked up?")

    bot.post_message(command.channel, "message text",  attachments=Atts.toJSON())