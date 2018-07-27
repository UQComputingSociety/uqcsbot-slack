from uqcsbot import bot, Command
import re
from uqcsbot.util.status_reacts import loading_status, success_status

API_URL = "https://memegen.link/"
# Many different characters need to be replaced in order to work in url format
# See the API_URL for details
REPLACEMENTS = {'_': '__', ' ': '_', r'\"': "''", '-': '--', '?': '~q', '%': '~p', '#': '~h', '/': '~s'}
VALID_NAMES = [
'names'
'aag',
'ackbar',
'afraid',
'ants',
'away',
'awesome',
'awesome-awkward',
'awkward',
'awkward-awesome',
'bad',
'badchoice',
'bd',
'bender',
'biw',
'blb',
'boat',
'both',
'bs',
'buzz',
'captain',
'cb',
'cbg',
'center',
'ch',
'chosen',
'crazypills',
'cryingfloor',
'disastergirl',
'dodgson',
'doge',
'drake',
'dsm',
'dwight',
'elf',
'ermg',
'fa',
'facepalm',
'fbf',
'fetch',
'fine',
'firsttry',
'fmr',
'fry',
'fwp',
'gandalf',
'ggg',
'grumpycat',
'hagrid',
'happening',
'hipster',
'icanhas',
'imsorry',
'inigo',
'interesting',
'ive',
'iw',
'jetpack',
'joker',
'jw',
'keanu',
'kermit',
'live',
'll',
'mb',
'mmm',
'money',
'mordor',
'morpheus',
'mw',
'nice',
'noidea',
'oag',
'officespace',
'older',
'oprah',
'patrick',
'philosoraptor',
'puffin',
'red',
'regret',
'remembers',
'rollsafe',
'sad-biden',
'sad-boehner',
'sad-bush',
'sad-clinton',
'sad-obama',
'sadfrog',
'saltbae',
'sarcasticbear',
'sb',
'scc',
'sf',
'sk',
'ski',
'snek',
'soa',
'sohappy',
'sohot',
'sparta',
'spongebob',
'ss',
'stew',
'success',
'tenguy',
'toohigh',
'tried',
'ugandanknuck',
'whatyear',
'winter',
'wonka',
'xy',
'yallgot',
'yodawg',
'yuno',

]
MEME_NAMES = """Ancient Aliens Guy: aag
It's A Trap!: ackbar
Afraid to Ask Andy: afraid
Do You Want Ants?: ants
Life... Finds a Way: away
Socially Awesome Penguin: awesome
Socially Awesome Awkward Penguin: awesome-awkward
Socially Awkward Penguin: awkward
Socially Awkward Awesome Penguin: awkward-awesome
You Should Feel Bad: bad
Milk Was a Bad Choice: badchoice
Butthurt Dweller: bd
I'm Going to Build My Own Theme Park: bender
Baby Insanity Wolf: biw
Bad Luck Brian: blb
I Should Buy a Boat Cat: boat
Why Not Both?: both
This is Bull, Shark: bs
X, X Everywhere: buzz
I am the Captain Now: captain
Confession Bear: cb
Comic Book Guy: cbg
What is this, a Center for Ants?!: center
Captain Hindsight: ch
You Were the Chosen One!: chosen
I Feel Like I'm Taking Crazy Pills: crazypills
Crying on Floor: cryingfloor
Disaster Girl: disastergirl
See? Nobody Cares: dodgson
Doge: doge
Drakeposting: drake
Dating Site Murderer: dsm
Schrute Facts: dwight
You Sit on a Throne of Lies: elf
Ermahgerd: ermg
Forever Alone: fa
Facepalm: facepalm
Foul Bachelor Frog: fbf
Stop Trying to Make Fetch Happen: fetch
This is Fine: fine
First Try!: firsttry
Fuck Me, Right?: fmr
Futurama Fry: fry
First World Problems: fwp
Confused Gandalf: gandalf
Good Guy Greg: ggg
Grumpy Cat: grumpycat
I Should Not Have Said That: hagrid
It's Happening: happening
Hipster Barista: hipster
I Can Has Cheezburger?: icanhas
Oh, I'm Sorry, I Thought This Was America: imsorry
Inigo Montoya: inigo
The Most Interesting Man in the World: interesting
Jony Ive Redesigns Things: ive
Insanity Wolf: iw
Nothing To Do Here: jetpack
It's Simple, Kill the Batman: joker
Probably Not a Good Idea: jw
Conspiracy Keanu: keanu
But That's None of My Business: kermit
Do It Live!: live
Laughing Lizard: ll
Member Berries: mb
Minor Mistake Marvin: mmm
Shut Up and Take My Money!: money
One Does Not Simply Walk into Mordor: mordor
Matrix Morpheus: morpheus
I Guarantee It: mw
So I Got That Goin' For Me, Which is Nice: nice
I Have No Idea What I'm Doing: noidea
Overly Attached Girlfriend: oag
That Would Be Great: officespace
An Older Code Sir, But It Checks Out: older
Oprah You Get a Car: oprah
Push it somewhere else Patrick: patrick
Philosoraptor: philosoraptor
Unpopular opinion puffin: puffin
Oh, Is That What We're Going to Do Today?: red
I Immediately Regret This Decision!: regret
Pepperidge Farm Remembers: remembers
Roll Safe: rollsafe
Sad Joe Biden: sad-biden
Sad John Boehner: sad-boehner
Sad George Bush: sad-bush
Sad Bill Clinton: sad-clinton
Sad Barack Obama: sad-obama
Sad Frog / Feels Bad Man: sadfrog
Salt Bae: saltbae
Sarcastic Bear: sarcasticbear
Scumbag Brain: sb
Sudden Clarity Clarence: scc
Sealed Fate: sf
Skeptical Third World Kid: sk
Super Cool Ski Instructor: ski
Skeptical Snake: snek
Seal of Approval: soa
I Would Be So Happy: sohappy
So Hot Right Now: sohot
This is Sparta!: sparta
Mocking Spongebob: spongebob
Scumbag Steve: ss
Baby, You've Got a Stew Going: stew
Success Kid: success
10 Guy: tenguy
The Rent Is Too Damn High: toohigh
At Least You Tried: tried
Ugandan Knuckles: ugandanknuck
What Year Is It?: whatyear
Winter is coming: winter
Condescending Wonka: wonka
X all the Y: xy
Y'all Got Any More of Them: yallgot
Xzibit Yo Dawg: yodawg
Y U NO Guy: yuno
"""

# TODO: Would be really simple to add custom UQCS memes


@bot.on_command("meme")
@loading_status
def handle_meme(command: Command):
    """
    !meme <meme name> "<top text>" "<bottom text>"

    For a full list of names: !meme names
    """
    channel = command.channel_id

    # Check if args where supplied and if not print the help
    if not command.has_arg():
        bot.post_message(channel, "Please run !help meme for usage")
        return

    name = command.arg.split()[0]
    if name not in VALID_NAMES:
        bot.post_message(channel, "The meme name is invalid. Try !meme names to get a list of all valid names")
        return

    args = get_meme_arguments(command.arg)

    if name.lower() == "names":
        send_meme_names(command)
        return
    elif len(args) == 2:
        top, bottom = args
    else:
        bot.post_message(channel, "You supplied the wrong number of args. Please run !help meme")
        return

    # Make an attachment linking to image
    image_url = API_URL + f"{name}/{top}/{bottom}.jpg"
    attachments = [{"text": "", "image_url": image_url}]
    bot.post_message(channel, "", attachments=attachments)


@success_status
def send_meme_names(command: Command):
    """Sends the full list of meme names to the users channel to avoid channel spam"""
    user_channel = bot.channels.get(command.user_id)
    bot.post_message(user_channel, MEME_NAMES)


def get_meme_arguments(input_args: str):
    """Gets the top and bottom text and returns them in a url friendly form that conforms with the api standards"""
    # This gets the text between the quotation marks (and ignores \")
    args = re.findall(r'"(.*?(?<!\\))"', input_args)

    # Replaces all the required characters to be url friendly
    url_friendly_args = []
    for arg in args:
        for old, new in REPLACEMENTS.items():
            arg = arg.replace(old, new)

        if arg == "":
            arg = "_"
        url_friendly_args.append(arg)
    print(url_friendly_args)
    return url_friendly_args
