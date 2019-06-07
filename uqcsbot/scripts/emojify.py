from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from typing import Dict, List

from collections import defaultdict
from random import shuffle, choice


@bot.on_command("emojify")
@loading_status
def handle_emojify(command: Command):
    '''
    `!emojify text` - converts text to emoji.
    '''
    master: Dict[str, List[str]] = defaultdict(lambda: ["grey_question"])

    master['A'] = ["adobe", "airbnb", "amazon", "anarchism", "arch", "atlassian", "office_access",
                   choice(["card-ace-clubs", "card-ace-diamonds",
                           "card-ace-hearts", "card-ace-spades"])]
    master['B'] = ["bhinking", "bitcoin", "blutes"]
    master['C'] = ["c", "clang", "cplusplus", "copyright"]
    master['D'] = ["d", "disney"]
    master['E'] = ["e", "ecorp", "emacs", "erlang", "ie10", "office_excel", "thonk_slow"]
    master['F'] = ["f", "facebook"]
    master['G'] = ["g+", "google", "nintendo_gamecube"]
    master['H'] = ["hackerrank", "homejoy"]
    master['I'] = ["information_source"]
    master['J'] = [choice(["card-jack-clubs", "card-jack-diamonds",
                           "card-jack-hearts", "card-jack-spades"]),
                   "hook"]
    master['K'] = [choice(["card-king-clubs", "card-king-diamonds",
                           "card-king-hearts", "card-king-spades"]),
                   "kickstarter", "kotlin"]
    master['L'] = ["l", "lime", "l_plate"]
    master['M'] = ["gmail", "maccas", "mcgrathnicol", "melange_mining", "mtg", "mxnet"]
    master['N'] = ["nano", "neovim", "netscape_navigator", "nginx", "nintendo_64", "office_onenote"]
    master['O'] = ["office_outlook", "oracle", "o_", "tetris_o", "ubuntu"]
    master['P'] = ["auspost", "office_powerpoint", "office_publisher",
                   "pinterest", "paypal", "producthunt"]
    master['Q'] = [choice(["card-queen-clubs", "card-queen-diamonds",
                           "card-queen-hearts", "card-queen-spades"]),
                   "quora", "quantium"]
    master['R'] = ["r-project", "rust", "redroom", "registered"]
    master['S'] = ["s", "skedulo", "stanford", "stripe_s", "sublime", "tetris_s"]
    master['T'] = ["tanda", choice(["telstra", "telstra-pink"]),
                   "tesla", "tetris_t", "torchwood", "tumblr"]
    master['U'] = ["uber", "uqu", "the_horns"]
    master['V'] = ["vim", "vue", "vuetify", "v"]
    master['W'] = ["office_word", "washio", "wesfarmers", "westpac",
                   "weyland_consortium", "wikipedia_w", "woolworths"]
    master['X'] = ["atlassian_old", "aginicx", "sonarr", "x-files", "xbox", "x", "flag-scotland"]
    master['Y'] = ["hackernews"]
    master['Z'] = ["tetris_z"]

    master['0'] = ["chrome", "suncorp", "disney_zero", "firefox", "mars", choice(["dvd", "cd"])]
    master['1'] = ["techone", "testtube", "thonk_ping", "first_place_medal"]
    master['2'] = [choice(["card-2-clubs", "card-2-diamonds", "card-2-hearts", "card-2-spades"]),
                   "second_place_medal"]
    master['3'] = [choice(["card-3-clubs", "card-3-diamonds", "card-3-hearts", "card-3-spades"]),
                   "css", "third_place_medal"]
    master['4'] = [choice(["card-4-clubs", "card-4-diamonds", "card-4-hearts"]), "card-4-spades"]
    master['5'] = [choice(["card-5-clubs", "card-5-diamonds", "card-5-hearts", "card-5-spades"]),
                   "html"]
    master['6'] = [choice(["card-6-clubs", "card-6-diamonds", "card-6-hearts", "card-6-spades"])]
    master['7'] = [choice(["card-7-clubs", "card-7-diamonds", "card-7-hearts", "card-7-spades"])]
    master['8'] = [choice(["card-8-clubs", "card-8-diamonds", "card-8-hearts", "card-8-spades"]),
                   "8ball"]
    master['9'] = [choice(["card-9-clubs", "card-9-diamonds", "card-9-hearts", "card-9-spades"])]

    master[' '] = ["whitespace"]

    master['@'] = ["whip"]
    master['#'] = ["slack_old", "csharp"]
    master['$'] = ["thonk_money", "moneybag"]
    master['^'] = ["this", "typographical_carrot", "arrow_up"]
    master['&'] = ["ampersand", "dnd"]
    master['*'] = ["day", "nab", "youtried", "msn_star", "rune_prayer"]
    master['-'] = ["no_entry"]
    master['+'] = ["tf2_medic", "flag-ch", "flag-england"]

    master['"'] = [choice(["ldquo", "rdquo"]), "pig_nose"]
    master['>'] = ["accenture", "implying", "plex", "powershell"]
    master['/'] = ["slash"]

    # master['Α'] = ["alpha"]
    # master['Β'] = ["beta"]
    # master['Λ'] = ["halflife", "haskell", "lambda", "racket"]
    # master['Σ'] = ["polymathian"]

    # master['…'] = ["lastpass"]
    # master['€'] = ["martian_euro"]
    # master['√'] = ["sqrt"]
    # master['∞'] = ["arduino", "visualstudio"]
    # master['∴'] = ["julia"]

    text = ""
    if command.has_arg():
        text = command.arg.upper()
    text = text.replace("&AMP;", "&")
    text = text.replace("&GT;", ">")

    emoji = {}
    for c in set(text):
        full, part = divmod(text.count(c), len(master[c]))
        shuffle(master[c])
        emoji[c] = full * master[c] + master[c][:part]
        shuffle(emoji[c])

    response = ""
    for c in text:
        response += ":"+emoji[c].pop()+":"

    bot.post_message(command.channel_id, response)
