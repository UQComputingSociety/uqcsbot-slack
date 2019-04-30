from uqcsbot import bot, Command
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from datetime import datetime as DT

def get_xml(state: str):
    source = {"NSW": "IDN11060", "ACT": "IDN11060", "NT": "IDD10207", "QLD": "IDQ11295", "SA": "IDS10044", "TAS": "IDT16710", "VIC": "IDV10753", "WA": "IDW14199"}
    try:
        data = urlopen("ftp://ftp.bom.gov.au/anon/gen/fwo/{}.xml".format(source[state]))
        root = ET.fromstring(data.read())
    except:
        return None
    return root
    

@bot.on_command('weather')
def handle_weather(command: Command):
    """
    `!weather [[state] location] [day]` - Returns the weather forcaset for location in the near future
    Defaults to day 0 (today) in Brisbane
    """

    arguments = command.arg.split(" ") if command.has_arg() else []

    # get number of days into the future
    if arguments and arguments[-1].lstrip('-+').isnumeric():
        future = int(arguments.pop())
    else:
        future = 0

    # get location
    if arguments:
        if arguments[0].upper() in ["NSW", "ACT", "NT", "QLD", "SA", "TAS", "VIC", "WA"]:
            state = arguments.pop(0).upper()
        else:
            state = "QLD"
        location = " ".join(arguments)
    else:
        state = "QLD"
        location = "Brisbane"

    # read BOM data
    root = get_xml(state)
    if root is None:
        bot.post_message(command.channel_id, "Could Not Retrieve BOM Data")
        return

    # find forecast
    node = root.find(".//area[@description='{}']".format(location))
    if node is None:
        bot.post_message(command.channel_id, "Location Not Found")
        return
    if node.get("type") != "location":
        bot.post_message(command.channel_id, "Location Given Is Region")
        return
    node = node.find(".//forecast-period[@index='{}']".format(future))
    if node is None:
        bot.post_message(command.channel_id, "No Forecast Available For That Day")
        return

    # write day name, "today" or "tomorrow"
    forcast_date = DT.strptime("".join(node.get('start-time-local').rsplit(":",1)), "%Y-%m-%dT%H:%M:%S%z").date()
    today_date = DT.now().date()
    date_delta = (forcast_date - today_date).days
    date_name = "Today" if date_delta == 0 else "Tomorrow" if date_delta == 1 else forcast_date.strftime("%A")
    response = "*{}'s Weather Forcast For {}*".format(date_name, location)

    # write overall forecast
    icon = node.find(".//element[@type='forecast_icon_code']")
    if icon is not None:
        icon = ["", "sunny", "clear", "partly-cloudy", "cloudy", "", "haze", "", "light-rain", "wind", "fog", "showers", "rain", "dust", "frost", "snow", "storm", "light-showers", "heavy-showers", "tropicalcyclone"][int(icon.text)]
        icon = ":bom_{}:".format(icon) if icon else ""
    descrip = node.find(".//text[@type='precis']")
    if descrip is not None:
        response += "\r\n{} {} {}".format(icon, descrip.text, icon)

    # write temperature
    temp_min = node.find(".//element[@type='air_temperature_minimum']")
    temp_max = node.find(".//element[@type='air_temperature_maximum']")
    if temp_min is not None and temp_max is not None:
        response += "\r\nTemperature: {}ºC - {}ºC".format(temp_min.text, temp_max.text)
    elif temp_min is not None:
        response += "\r\nMinimum Temperature: {}ºC".format(temp_min.text)
    elif temp_max is not None:
        response += "\r\nMaximum Temperature: {}ºC".format(temp_max.text)

    # write precipitation
    rain_range = node.find(".//element[@type='precipitation_range']")
    precip_prob = node.find(".//text[@type='probability_of_precipitation']")
    if rain_range is not None and precip_prob is not None:
        response += "\r\n{} Chance of Precipitation; {}".format(precip_prob.text, rain_range.text)
    elif precip_prob is not None:
        response += "\r\n{} Chance of Precipitation".format(precip_prob.text)

    # post
    bot.post_message(command.channel_id, response)
