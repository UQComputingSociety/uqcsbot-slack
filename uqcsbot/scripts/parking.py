from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from urllib.request import urlopen
from re import findall
from typing import Union


def get_pf_parking_data() -> Union[str, None]:
    """
    Returns a parking HTML document from the UQ P&F website
    """
    try:
        data = urlopen("https://pg.pf.uq.edu.au/").read().decode("utf-8")
    except Exception:
        return None
    return data


@bot.on_command("parking")
@loading_status
def handle_parking(command: Command) -> None:
    """
    `!parking [all]` - Displays how many car parks are available at UQ St. Lucia
    By default, only dispalys casual parking availability
    """

    if command.has_arg() and command.arg.lower() == "all":
        permit = True
    else:
        permit = False

    # read parking data
    data = get_pf_parking_data()
    if data is None:
        bot.post_message(command.channel_id, "Could Not Retrieve Parking Data")
        return

    response = ["*Available Parks at UQ St. Lucia*"]
    names = {"P1": "P1 - Warehouse (14P Daily)", "P2": "P2 - Space Bank (14P Daily)",
             "P3": "P3 - Multi-Level West (Staff)", "P4": "P4 - Multi-Level East (Staff)",
             "P6": "P6 - Hartley Teakle (14P Hourly)", "P7": "P7 - DustBowl (14P Daily)",
             "P7 UC": "P7 - Keith Street (14P Daily Capped)",
             "P8 L1": "P8 - Athletics Basement (14P Daily)",
             "P8 L2": "P8 - Athletics Roof (14P Daily)", "P9": "P9 - Boatshed (14P Daily)",
             "P10": "P10 - UQ Centre & Playing Fields (14P Daily/14P Daily Capped)",
             "P11 L1": "P11 - Conifer Knoll Lower (Staff)",
             "P11 L2": "P11 - Conifer Knoll Upper (Staff)",
             "P11 L3": "P11 - Conifer Knoll Roof (14P Daily Restricted)"}
    catagory = lambda x: "No" if x == "FULL" else "Few" if x == "NEARLY FULL" else x

    # find parks
    areas = findall(r"<tr>\W*<td class='zone'>(.*)<\/td>\W*<td class='.*\n?'>(.*)\n?<\/td>" +
                    r"\W*<td class='.*\n?'>(.*)\n?<\/td>\W*<\/tr>", str(data))
    for a in areas:
        if a[2]:
            response.append(f"{catagory(a[2])} Carparks Availible in {names[a[0]]}")
        elif permit and a[1]:
            response.append(f"{catagory(a[1])} Carparks Availible in {names[a[0]]}")
    bot.post_message(command.channel_id, "\n".join(response))
