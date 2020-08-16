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
    master: Dict[str, List[str]] = defaultdict(lambda: [":grey_question:"])

    # letters
    master['A'] = [":adobe:", ":airbnb:", ":amazon:", ":anarchism:",
                   ":arch:", ":atlassian:", ":office_access:", ":capital_a_agile:",
                   choice([":card-ace-clubs:", ":card-ace-diamonds:",
                           ":card-ace-hearts:", ":card-ace-spades:"])]
    master['B'] = [":bhinking:", ":bitcoin:", ":blutes:"]
    master['C'] = [":c:", ":clang:", ":cplusplus:", ":copyright:", ":clipchamp:"]
    master['D'] = [":d:", ":disney:", ":deloitte:"]
    master['E'] = [":ecorp:", ":emacs:", ":erlang:", ":ie10:", ":thonk_slow:", ":edge:",
                   ":expedia_group:"]
    master['F'] = [":f:", ":facebook:", ":flutter:", ":figma:"]
    master['G'] = [":g+:", ":google:", ":nintendo_gamecube:", ":gatsbyjs:"]
    master['H'] = [":hackerrank:", ":homejoy:"]
    master['I'] = [":information_source:", ":indoorooshs:"]
    master['J'] = [":hook:", choice([":card-jack-clubs:", ":card-jack-diamonds:",
                                     ":card-jack-hearts:", ":card-jack-spades:"])]
    master['K'] = [":kickstarter:", ":kotlin:",
                   choice([":card-king-clubs:", ":card-king-diamonds:",
                           ":card-king-hearts:", ":card-king-spades:"])]
    master['L'] = [":l:", ":lime:", ":l_plate:"]
    master['M'] = [":gmail:", ":maccas:", ":mcgrathnicol:", ":melange_mining:", ":mtg:", ":mxnet:",
                   ":jmod:"]
    master['N'] = [":nano:", ":neovim:", ":netscape_navigator:",
                   ":nginx:", ":nintendo_64:", ":office_onenote:", ":netflix-n:"]
    master['O'] = [":office_outlook:", ":oracle:", ":o_:", ":tetris_o:", ":ubuntu:",
                   choice([":portal_blue:", ":portal_orange:"])]
    master['P'] = [":auspost:", ":office_powerpoint:", ":office_publisher:",
                   ":pinterest:", ":paypal:", ":producthunt:", ":uqpain:"]
    master['Q'] = [":quora:", ":quantium:", choice([":card-queen-clubs:", ":card-queen-diamonds:",
                                                    ":card-queen-hearts:", ":card-queen-spades:"])]
    master['R'] = [":r-project:", ":rust:", ":redroom:", ":registered:"]
    master['S'] = [":s:", ":skedulo:", ":stanford:", ":stripe_s:", ":sublime:", ":tetris_s:"]
    master['T'] = [":tanda:", choice([":telstra:", ":telstra-pink:"]),
                   ":tesla:", ":tetris_t:", ":torchwood:", ":tumblr:", ":nyt:"]
    master['U'] = [":uber:", ":uqu:", ":the_horns:", ":proctoru:", ":ubiquiti:"]
    master['V'] = [":vim:", ":vue:", ":vuetify:", ":v:"]
    master['W'] = [":office_word:", ":washio:", ":wesfarmers:", ":westpac:",
                   ":weyland_consortium:", ":wikipedia_w:", ":woolworths:"]
    master['X'] = [":atlassian_old:", ":aginicx:", ":sonarr:", ":x-files:", ":xbox:",
                   ":x:", ":flag-scotland:", ":office_excel:"]
    master['Y'] = [":hackernews:"]
    master['Z'] = [":tetris_z:"]

    # numbers
    master['0'] = [":chrome:", ":suncorp:", ":disney_zero:", ":firefox:",
                   ":mars:", ":0_:", choice([":dvd:", ":cd:"])]
    master['1'] = [":techone:", ":testtube:", ":thonk_ping:", ":first_place_medal:",
                   ":critical_fail:"]
    master['2'] = [":second_place_medal:", choice([":card-2-clubs:", ":card-2-diamonds:",
                                                   ":card-2-hearts:", ":card-2-spades:"])]
    master['3'] = [":css:", ":third_place_medal:", choice([":card-3-clubs:", ":card-3-diamonds:",
                                                           ":card-3-hearts:", ":card-3-spades:"])]
    master['4'] = [choice([":card-4-clubs:", ":card-4-diamonds:",
                           ":card-4-hearts:"]), ":card-4-spades:"]
    master['5'] = [":html:", choice([":card-5-clubs:", ":card-5-diamonds:",
                                     ":card-5-hearts:", ":card-5-spades:"])]
    master['6'] = [choice([":card-6-clubs:", ":card-6-diamonds:",
                           ":card-6-hearts:", ":card-6-spades:"])]
    master['7'] = [choice([":card-7-clubs:", ":card-7-diamonds:",
                           ":card-7-hearts:", ":card-7-spades:"])]
    master['8'] = [":8ball:", choice([":card-8-clubs:", ":card-8-diamonds:",
                                      ":card-8-hearts:", ":card-8-spades:"])]
    master['9'] = [choice([":card-9-clubs:", ":card-9-diamonds:",
                           ":card-9-hearts:", ":card-9-spades:"])]

    # whitespace
    master[' '] = [":whitespace:"]
    master['\n'] = ["\n"]

    # other ascii characters (sorted by ascii value)
    master['!'] = [":exclamation:"]
    master['"'] = [choice([":ldquo:", ":rdquo:"]), ":pig_nose:"]
    master['\''] = [":apostrophe:"]
    master['#'] = [":slack_old:", ":csharp:"]
    master['$'] = [":thonk_money:", ":moneybag:"]
    # '&' converts to '&AMP;'
    master['&'] = [":ampersand:", ":dnd:"]
    master['('] = [":lparen:"]
    master[')'] = [":rparen:"]
    master['*'] = [":day:", ":nab:", ":youtried:", ":msn_star:", ":rune_prayer:", ":wolfram:",
                   ":shuriken:", ":mtg_s:"]
    master['+'] = [":tf2_medic:", ":flag-ch:", ":flag-england:"]
    master['-'] = [":no_entry:"]
    master['.'] = [":black_small_square:"]
    master[','] = [":comma:"]
    master['/'] = [":slash:"]
    master[';'] = [":semi-colon:"]
    # '>' converts to '&GT;'
    master['>'] = [":accenture:", ":implying:", ":plex:", ":powershell:"]
    master['?'] = [":question:"]
    master['@'] = [":whip:"]
    master['^'] = [":this:", ":typographical_carrot:", ":arrow_up:",
                   ":this_but_it's_an_actual_caret:"]
    master['~'] = [":wavy_dash:"]

    # slack/uqcsbot convert the following to other symbols

    # greek letters
    # 'Α' converts to 'A'
    master['Α'] = [":alpha:"]
    # 'Β' converts to 'B'
    master['Β'] = [":beta:"]
    # 'Δ' converts to 'D'
    master['Δ'] = [":optiver:"]
    # 'Λ' converts to 'L'
    master['Λ'] = [":halflife:", ":haskell:", ":lambda:", ":racket:"]
    # 'Π' converts to 'P'
    master['Π'] = [":pi:"]
    # 'Σ' converts to 'S'
    master['Σ'] = [":polymathian:", ":sigma:"]

    # other symbols (sorted by unicode value)
    # '…' converts to '...'
    master['…'] = [":lastpass:"]
    # '€' converts to 'EUR'
    master['€'] = [":martian_euro:"]
    # '√' converts to '[?]'
    master['√'] = [":sqrt:"]
    # '∞' converts to '[?]'
    master['∞'] = [":arduino:", ":visualstudio:", ":infinitely:"]
    # '∴' converts to '[?]'
    master['∴'] = [":julia:"]

    master['人'] = [":人:"]

    text = ""
    if command.has_arg():
        text = command.arg.upper()
    # revert HTML conversions
    text = text.replace("&GT;", ">")
    text = text.replace("&LT;", "<")
    text = text.replace("&AMP;", "&")

    lexicon = {}
    for character in set(text+'…'):
        full, part = divmod((text+'…').count(character), len(master[character]))
        shuffle(master[character])
        lexicon[character] = full * master[character] + master[character][:part]
        shuffle(lexicon[character])

    ellipsis = lexicon['…'].pop()

    response = ""
    for character in text:
        emoji = lexicon[character].pop()
        if len(response + emoji + ellipsis) > 4000:
            response += ellipsis
            break
        response += emoji

    bot.post_message(command.channel_id, response)
