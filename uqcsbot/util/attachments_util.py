from typing import List, Optional
from enum import Enum
from validators import url as validateURL
import json

# Link buttons and actions like this are specified here https://api.slack.com/docs/message-attachments#link_buttons
# Describes individual types actions
class ButtonStyle(Enum):
     STYLE_PRIMARY = "primary"
     STYLE_DANGER = "danger"

class AttachmentAction:
    action_type:str
    action_text:str
    action_url:str
    action_type:str = None

    def validate(self):
        return (not validateURL(self.action_url)) or (self.action_type == None)

class LinkButton(AttachmentAction):
    action_type:str = "button"
    
    # Optional
    button_style:ButtonStyle = ButtonStyle.STYLE_PRIMARY

    def __init__(self, text:str, url:str, button_style:Optional[ButtonStyle]):
        self.action_text = text
        self.action_url = url
        if not button_style == None:
            self.button_style = button_style

class AttachmentActions:
    actions_fallback:str
    list_actions:List[AttachmentAction]
    
    def __init__(self, fallback:str, actions:List[AttachmentAction]):
        self.actions_fallback = fallback
        self.list_actions = actions

class AttachmentFields:
    field_title:str
    field_value:str

    # Optional
    # This param specifies if the field is skinny
    #  enough to be shown beside others
    field_short:bool = False

    def __init__(self, title:str, value:str, short:Optional[str]):
        self.field_title = title
        self.field_value = value
        if not short == None:
            self.field_short = short


class AttachmentColour(Enum):
    COLOUR_GOOD = "good"
    COLOUR_WARNING = "warning"
    COLOUR_DANGER = "danger"

# https://api.slack.com/docs/message-attachments
class Attachment:
    # Non Optional Params (can be "")
    attachment_fallback:str
    attachment_text:str

    # Optional Params
    attachment_color:AttachmentColour = None
    attachment_pretext:str = None
    attachment_title:str = None
    # Supplying the link will automatically hyperlink the title
    attachment_title_link:str = None
    # Should have at most 2 or 3 (as per the docs)
    attachment_fields:List[AttachmentFields] = None
    attachment_footer:str = None
    attachment_actions:AttachmentActions = None # At most 5

    # Unimplemented Params
    # Author paramaters
    # Image URL
    # Thumb URL
    # Footer Icon
    # ts (timestamp)

    def __init__(self, fallback:str, text:str):
        self.attachment_fallback = fallback
        self.attachment_text = text

    def validate(self) -> bool:
        if not self.attachment_title_link == None:
            if self.attachment_title == None:
                # Should only define the link when the title is set
                return False
            if not validateURL(self.attachment_title_link):
                # Attachment Link should be valid if not None
                return None
        if not self.attachment_fields == None:
            # There is the strongly suggested limit of 3
            # This limit could be removed if needs be,
            # or some strict_validate could be added
            # to ignore this item
            if self.attachment_fields > 3:
                return False
        if not self.attachment_actions == None:
            actionsCount:int = len(self.attachment_actions.list_actions)
            # Should not add empty actions list
            if actionsCount == 0:
                return False
            # Should not have more than 5 actions
            if actionsCount > 5:
                return False

            # Validates each of the actions to make sure they are valid
            for act in self.attachment_actions.list_actions:
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
        for Att in self.list_attachments:
            if Att.validate() == False:
                return False
        return True

# Foo = Attachments_Util("Fallback","text")
# bot.logger.error(Foo.validate())
# bot.logger.error("here?")
        


