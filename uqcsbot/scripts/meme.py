from uqcsbot import bot, Command
import re
from uqcsbot.utils.command_utils import loading_status, success_status, UsageSyntaxException
from urllib.parse import quote

API_URL = "https://memegen.link/"
# Many different characters need to be replaced in order to work in url format
# See the API_URL for details
REPLACEMENTS = str.maketrans({'_': '__', ' ': '_', '-': '--', '?': '~q',
                              '%': '~p', '#': '~h', '/': '~s'})
MEME_NAMES = {
    "aag": "Ancient Aliens Guy",
    "ackbar": "It's A Trap!",
    "afraid": "Afraid to Ask Andy",
    "ants": "Do You Want Ants?",
    "away": "Life... Finds a Way",
    "awesome": "Socially Awesome Penguin",
    "awesome-awkward": "Socially Awesome Awkward Penguin",
    "awkward": "Socially Awkward Penguin",
    "awkward-awesome": "Socially Awkward Awesome Penguin",
    "bad": "You Should Feel Bad",
    "badchoice": "Milk Was a Bad Choice",
    "bd": "Butthurt Dweller",
    "bender": "I'm Going to Build My Own Theme Park",
    "biw": "Baby Insanity Wolf",
    "blb": "Bad Luck Brian",
    "boat": "I Should Buy a Boat Cat",
    "both": "Why Not Both?",
    "bs": "This is Bull, Shark",
    "buzz": "X, X Everywhere",
    "captain": "I am the Captain Now",
    "cb": "Confession Bear",
    "cbg": "Comic Book Guy",
    "center": "What is this, a Center for Ants?!",
    "ch": "Captain Hindsight",
    "chosen": "You Were the Chosen One!",
    "crazypills": "I Feel Like I'm Taking Crazy Pills",
    "cryingfloor": "Crying on Floor",
    "disastergirl": "Disaster Girl",
    "dodgson": "See? Nobody Cares",
    "doge": "Doge",
    "drake": "Drakeposting",
    "dsm": "Dating Site Murderer",
    "dwight": "Schrute Facts",
    "elf": "You Sit on a Throne of Lies",
    "ermg": "Ermahgerd",
    "fa": "Forever Alone",
    "facepalm": "Facepalm",
    "fbf": "Foul Bachelor Frog",
    "fetch": "Stop Trying to Make Fetch Happen",
    "fine": "This is Fine",
    "firsttry": "First Try!",
    "fmr": "Fuck Me, Right?",
    "fry": "Futurama Fry",
    "fwp": "First World Problems",
    "gandalf": "Confused Gandalf",
    "ggg": "Good Guy Greg",
    "grumpycat": "Grumpy Cat",
    "hagrid": "I Should Not Have Said That",
    "happening": "It's Happening",
    "hipster": "Hipster Barista",
    "icanhas": "I Can Has Cheezburger?",
    "imsorry": "Oh, I'm Sorry, I Thought This Was America",
    "inigo": "Inigo Montoya",
    "interesting": "The Most Interesting Man in the World",
    "ive": "Jony Ive Redesigns Things",
    "iw": "Insanity Wolf",
    "jetpack": "Nothing To Do Here",
    "joker": "It's Simple, Kill the Batman",
    "jw": "Probably Not a Good Idea",
    "keanu": "Conspiracy Keanu",
    "kermit": "But That's None of My Business",
    "live": "Do It Live!",
    "ll": "Laughing Lizard",
    "mb": "Member Berries",
    "mmm": "Minor Mistake Marvin",
    "money": "Shut Up and Take My Money!",
    "mordor": "One Does Not Simply Walk into Mordor",
    "morpheus": "Matrix Morpheus",
    "mw": "I Guarantee It",
    "nice": "So I Got That Goin' For Me, Which is Nice",
    "noidea": "I Have No Idea What I'm Doing",
    "oag": "Overly Attached Girlfriend",
    "officespace": "That Would Be Great",
    "older": "An Older Code Sir, But It Checks Out",
    "oprah": "Oprah You Get a Car",
    "patrick": "Push it somewhere else Patrick",
    "philosoraptor": "Philosoraptor",
    "puffin": "Unpopular opinion puffin",
    "red": "Oh, Is That What We're Going to Do Today?",
    "regret": "I Immediately Regret This Decision!",
    "remembers": "Pepperidge Farm Remembers",
    "rollsafe": "Roll Safe",
    "sad-biden": "Sad Joe Biden",
    "sad-boehner": "Sad John Boehner",
    "sad-bush": "Sad George Bush",
    "sad-clinton": "Sad Bill Clinton",
    "sad-obama": "Sad Barack Obama",
    "sadfrog": "Sad Frog / Feels Bad Man",
    "saltbae": "Salt Bae",
    "sarcasticbear": "Sarcastic Bear",
    "sb": "Scumbag Brain",
    "scc": "Sudden Clarity Clarence",
    "sf": "Sealed Fate",
    "sk": "Skeptical Third World Kid",
    "ski": "Super Cool Ski Instructor",
    "snek": "Skeptical Snake",
    "soa": "Seal of Approval",
    "sohappy": "I Would Be So Happy",
    "sohot": "So Hot Right Now",
    "sparta": "This is Sparta!",
    "spongebob": "Mocking Spongebob",
    "ss": "Scumbag Steve",
    "stew": "Baby, You've Got a Stew Going",
    "success": "Success Kid",
    "tenguy": "10 Guy",
    "toohigh": "The Rent Is Too Damn High",
    "tried": "At Least You Tried",
    "ugandanknuck": "Ugandan Knuckles",
    "whatyear": "What Year Is It?",
    "winter": "Winter is coming",
    "wonka": "Condescending Wonka",
    "xy": "X all the Y",
    "yallgot": "Y'all Got Any More of Them",
    "yodawg": "Xzibit Yo Dawg",
    "yuno": "Y U NO Guy",
}

# TODO: Would be really simple to add custom UQCS memes


@bot.on_command("meme")
@loading_status
def handle_meme(command: Command):
    """
    `!meme <names | (<MEME NAME> "<TOP TEXT>" "<BOTTOM TEXT>")>`
    Generates a meme of the given format with the provided top and
    bottom text. For a full list of formats, try `!meme names`.
    """
    channel = command.channel_id

    if not command.has_arg():
        raise UsageSyntaxException()

    name = command.arg.split()[0].lower()
    if name == "names":
        send_meme_names(command)
        return
    elif name not in MEME_NAMES.keys():
        bot.post_message(channel, "The meme name is invalid. "
                         "Try `!meme names` to get a list of all valid names")
        return

    args = get_meme_arguments(command.arg)
    if len(args) != 2:
        raise UsageSyntaxException()

    # Make an attachment linking to image
    top, bottom = args
    image_url = API_URL + f"{quote(name)}/{quote(top)}/{quote(bottom)}.jpg"
    attachments = [{"text": "", "image_url": image_url}]
    bot.post_message(channel, "", attachments=attachments)


@success_status
def send_meme_names(command: Command):
    """
    Sends the full list of meme names to the users channel to avoid channel spam
    """
    user_channel = bot.channels.get(command.user_id)
    names_text = "\n".join((f"{full_name}: {name}" for (name, full_name) in MEME_NAMES.items()))
    attachments = [{'text': names_text, 'title': "Meme Names:"}]
    bot.post_message(user_channel, "", attachments=attachments)


def get_meme_arguments(input_args: str):
    """
    Gets the top and bottom text and returns them in a
    url friendly form that conforms with the api standards
    """
    # This gets the text between the quotation marks (and ignores \")
    args = re.findall(r'"(.*?(?<!\\))"', input_args)

    # Replaces all the required characters to be url friendly
    url_friendly_args = []
    for arg in args:
        arg = arg.translate(REPLACEMENTS)
        # the translate function won't properly handle the '\"' character so we do it explicitly
        arg = arg.replace(r'\"', "''")

        if arg == "":
            arg = "_"

        url_friendly_args.append(arg)

    return url_friendly_args
