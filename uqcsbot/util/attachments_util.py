from typing import List, Optional
from enum import Enum
from validators import url as validateURL
import json

# Link buttons and actions like this are specified here https://api.slack.com/docs/message-attachments#link_buttons
# Describes individual types actions
class ButtonStyle(Enum):
     STYLE_PRIMARY = "primary"
     STYLE_DANGER = "danger"

class ActionType(Enum):
    TYPE_BUTTON = "button"

class AttachmentAction:
    action_type:str
    action_text:str
    action_url:str

    # Optional Depending on if it is used in the action type
    button_style:str = None

    def validate(self):
        return (not validateURL(self.action_url)) or (self.action_type == None)

class LinkButtonAction(AttachmentAction):   
    def __init__(self, text:str, url:str, button_style:Optional[ButtonStyle]):
        self.action_type = ActionType.TYPE_BUTTON.value
        self.action_text = text
        self.action_url = url
        if not button_style == None:
            self.button_style = button_style.value
        else:
            button_style = ButtonStyle.STYLE_PRIMARY.value

    def set_button_style(self,bs:ButtonStyle):
        self.button_style = bs.value

class AttachmentField:
    field_title:str
    field_value:str

    # Optional
    # This param specifies if the field is skinny
    #  enough to be shown beside others
    field_short:bool = False

    def __init__(self, title:str, value:str, short:Optional[bool]):
        self.field_title = title
        self.field_value = value
        if not short == None:
            self.field_short = short


class AttachmentColor(Enum):
    COLOUR_GOOD = "good"
    COLOUR_WARNING = "warning"
    COLOUR_DANGER = "danger"

# https://api.slack.com/docs/message-attachments
class Attachment:
    # Non Optional Params (can be "")
    attachment_fallback:str
    attachment_text:str

    # Optional Params
    attachment_color:str = None
    attachment_pretext:str = None
    attachment_title:str = None
    # Supplying the link will automatically hyperlink the title
    attachment_title_link:str = None
    # Should have at most 2 or 3 (as per the docs)
    attachment_fields:List[AttachmentField] = []
    attachment_footer:str = None
    attachment_actions:List[AttachmentAction] = [] # At most 5

    # Unimplemented Params
    # Author paramaters
    # Image URL
    # Thumb URL
    # Footer Icon
    # ts (timestamp)

    def __init__(self, fallback:str, text:str):
        self.attachment_fallback = fallback
        self.attachment_text = text

    def set_color(self, ac:AttachmentColor):
        self.attachment_color = ac.value

    def validate(self) -> bool:
        if not self.attachment_title_link == None:
            if self.attachment_title == None:
                # Should only define the link when the title is set
                return False
            if not validateURL(self.attachment_title_link):
                # Attachment Link should be valid if not None
                return None
        if not self.attachment_fields == []:
            # There is the strongly suggested limit of 3
            # This limit could be removed if needs be,
            # or some strict_validate could be added
            # to ignore this item
            if len(self.attachment_fields) > 3:
                return False
        if not self.attachment_actions == []:
            actionsCount:int = len(self.attachment_actions)
            # Should not add empty actions list
            if actionsCount == 0:
                return False
            # Should not have more than 5 actions
            if actionsCount > 5:
                return False

            # Validates each of the actions to make sure they are valid
            act:AttachmentAction
            for act in self.attachment_actions:
                if not act.validate:
                    return False

        return True
    

class Attachments_Util:
    list_attachments:List[Attachment] = None

    def __init__(self):
        self.list_attachments = []
    
    def add_attachment(self,att:Attachment):
        self.list_attachments.append(att)

    # Required due to the inability to define the
    # property type without conflict 
    class Encoder(json.JSONEncoder):
        def default(self, o):
            return {"_".join(k.split("_")[1:]): v for k, v in vars(o).items()}

    def toJSON(self):
        initalJSON:str = json.dumps(self, cls=Attachments_Util.Encoder)
        # This will have an extra layer of un-needed and unwanted wrapping
        # Remove the param decl and the {
        initalJSON = initalJSON[len("\'{\"attachments\":"):]
        # Remove the last }
        initalJSON = initalJSON[:-1]
        return initalJSON

    def validate(self) -> bool:
        attCount = len(self.list_attachments)
        if (attCount > 20) or (attCount == 0):
            return False
        for Att in self.list_attachments:
            if Att.validate() == False:
                return False
        return True



# # Some example ways to use this
# from uqcsbot import bot, Command
# from uqcsbot.util.attachments_util import *
# import json


# @bot.on_command("button")
# def handle_button(command: Command):
#     '''
#     `!button` - Shows the test button.
#     '''
#     Att1 = Attachment("Fallback1","attachement text 1")
#     Att1.attachment_title = "Some title text!"
#     Att1.attachment_title_link = "https://github.com/UQComputingSociety/uqcsbot/issues/311"
#     Att1.attachment_footer = "Small footer?"
#     Att1.set_color(AttachmentColor.COLOUR_GOOD)

#     Att2 = Attachment("Fallback2","attachement text 2")
#     lb1 = LinkButtonAction("Btn1","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
#     lb2 = LinkButtonAction("Btn2","https://github.com/UQComputingSociety/uqcsbot/issues/311", ButtonStyle.STYLE_DANGER)
#     lb3 = LinkButtonAction("Btn3","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
#     lb4 = LinkButtonAction("Btn4","https://github.com/UQComputingSociety/uqcsbot/issues/311", ButtonStyle.STYLE_DANGER)
#     lb5 = LinkButtonAction("Btn5","https://github.com/UQComputingSociety/uqcsbot/issues/311", None)
#     Att2.attachment_actions = [lb1,lb2,lb3,lb4,lb5]
#     Att2.set_color(AttachmentColor.COLOUR_DANGER)

#     Att3 = Attachment("Fallback3","attachement text 3")
#     Att3.set_color(AttachmentColor.COLOUR_WARNING)
#     Att3.attachment_pretext = "pretext for attachment 3 looks like normal text, sort of..."
#     f1 = AttachmentField("Title 1","foo",False)
#     f2 = AttachmentField("Title 2","bar",True)
#     f3 = AttachmentField("Title 3","baz",True)
#     Att3.attachment_fields = [f1, f2, f3]

#     # Monster
#     Att4 = Attachment("Fallback4", "I wonder what happens if I put all the things together?")
#     Att4.attachment_title = "Some title text attachment 4!"
#     Att4.attachment_title_link = "https://github.com/UQComputingSociety/uqcsbot/issues/311"
#     Att4.attachment_footer = "Small footer for attachment 4?"
#     Att4.set_color(AttachmentColor.COLOUR_DANGER)
#     Att4.attachment_actions = [lb1,lb2,lb3,lb4,lb5]
#     Att4.attachment_pretext = "pretext for attachment 4 looks like normal text, sort of..."
#     Att4.attachment_fields = [f1, f2, f3]


#     Atts = Attachments_Util()
#     Atts.add_attachment(Att1)
#     Atts.add_attachment(Att2)
#     Atts.add_attachment(Att3)
#     Atts.add_attachment(Att4)

#     if Atts.validate() == False:
#         bot.logger.error("Fucked up?")

#     bot.post_message(command.channel, "message text",  attachments=Atts.toJSON())


# @bot.on_command("buttonArray")
# def handle_button_array(command: Command):
#     '''
#     `!buttonArray` - Shows the most amount of buttons.
#     '''

#     Atts = Attachments_Util()
#     AttachmentArray = []
#     for i in range(20):
#         attachment = Attachment("","")
#         btnArray = []
#         for j in range(5):
#             btnArray.append(LinkButtonAction(f"{i:02d},{j:02d}","https://github.com/UQComputingSociety/uqcsbot/issues/311", None))
#         attachment.attachment_actions = btnArray
#         Atts.add_attachment(attachment)

#     if Atts.validate() == False:
#         bot.logger.error("Fucked up?")

#     bot.post_message(command.channel, "message text",  attachments=Atts.toJSON())

