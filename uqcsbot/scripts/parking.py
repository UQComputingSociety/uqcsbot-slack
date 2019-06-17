from uqcsbot import bot, Command
from uqcsbot.utils.command_utils import loading_status
from typing import Tuple

import requests
from bs4 import BeautifulSoup


def get_pf_parking_data() -> Tuple[int, str]:
    """
    Returns a parking HTML document from the UQ P&F website
    """
    page = requests.get("https://pg.pf.uq.edu.au/")
    return (page.status_code, page.text)


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
    code, data = get_pf_parking_data()
    if code != 200:
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

    def category(fill):
        if fill.upper() == "FULL":
            return "No"
        if fill.upper() == "NEARLY FULL":
            return "Few"
        return fill

    # find parks
    table = BeautifulSoup(data, 'html.parser').find("table", attrs={"id": "parkingAvailability"})
    rows = table.find_all("tr")[1:]
    # split and join for single space whitespace
    areas = [[" ".join(i.get_text().strip().split()) for i in j.find_all("td")] for j in rows]

    for area in areas:
        if area[2]:
            response.append(f"{category(area[2])} Carparks Availible in {names[area[0]]}")
        elif permit and area[1]:
            response.append(f"{category(area[1])} Carparks Availible in {names[area[0]]}")
    bot.post_message(command.channel_id, "\n".join(response))
