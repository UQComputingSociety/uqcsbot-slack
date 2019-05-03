from uqcsbot import bot, Command
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from datetime import datetime as DT
from typing import Union, Tuple


def get_xml(state: str) -> Union[None, ET.Element]:
    """
    Get BOM data as an XML for a given state
    """
    source = {"NSW": "IDN11060", "ACT": "IDN11060", "NT": "IDD10207", "QLD": "IDQ11295",
              "SA": "IDS10044", "TAS": "IDT16710", "VIC": "IDV10753", "WA": "IDW14199"}
    try:
        data = urlopen(f"ftp://ftp.bom.gov.au/anon/gen/fwo/{source[state]}.xml")
        root = ET.fromstring(data.read())
    except Exception:
        return None
    return root


def process_arguments(arguments: str) -> Tuple[str, str, str]:
    """
    Process the arguments given to !weather, dividing them into state, location and future
    Uses default of QLD, Brisbane and 0 if not given
    """
    args = arguments.split(" ") if arguments else []
    if args and args[-1].lstrip('-+').isnumeric():
        future = int(args.pop())
    else:
        future = 0

    # get location
    if args:
        if args[0].upper() in ["NSW", "ACT", "NT", "QLD", "SA", "TAS", "VIC", "WA"]:
            state = args.pop(0).upper()
        else:
            state = "QLD"
        location = " ".join(args)
    else:
        state = "QLD"
        location = "Brisbane"

    return state, location, future


def find_location(root: ET.Element, location: str, future: int) \
                  -> Tuple[Union[None, ET.Element], Union[None, str]]:
    """
    Rreturns the XML for a given the location and how far into the future
    """
    node = root.find(f".//area[@description='{location}']")
    if node is None:
        return None, "Location Not Found"
    if node.get("type") != "location":
        return None, "Location Given Is Region"
    node = node.find(f".//forecast-period[@index='{future}']")
    if node is None:
        return None, "No Forecast Available For That Day"
    return node, None


def response_header(node: ET.Element, location: str) -> str:
    """
    Returns the response header, in the form "{Location}'s Weather Forcast For {Day}"
    """
    forcast_date = DT.strptime("".join(node.get('start-time-local')
                                       .rsplit(":", 1)), "%Y-%m-%dT%H:%M:%S%z").date()
    today_date = DT.now().date()
    date_delta = (forcast_date - today_date).days
    if date_delta == 0:
        date_name = "Today"
    elif date_delta == 1:
        date_name = "Tomorrow"
    elif date_delta == -1:
        # can happen during the witching hours
        date_name = "Yesterday"
    else:
        date_name = forcast_date.strftime("%A")
    return f"*{date_name}'s Weather Forcast For {location}*"


def response_overall(node: ET.Element) -> str:
    """
    Returns the overall forcast
    """
    icon_code = node.find(".//element[@type='forecast_icon_code']")
    if icon_code is not None:
        icon = ["", "sunny", "clear", "partly-cloudy", "cloudy", "", "haze", "", "light-rain",
                "wind", "fog", "showers", "rain", "dust", "frost", "snow", "storm",
                "light-showers", "heavy-showers", "tropicalcyclone"][int(icon_code.text)]
        icon = f":bom_{icon}:" if icon else ""
    descrip = node.find(".//text[@type='precis']")
    if descrip is not None:
        return f"{icon} {descrip.text} {icon}"
    return ""


def response_temperature(node: ET.Element) -> str:
    """
    Returns the temperature forecast
    """
    temp_min = node.find(".//element[@type='air_temperature_minimum']")
    temp_max = node.find(".//element[@type='air_temperature_maximum']")
    if temp_min is not None and temp_max is not None:
        return f"Temperature: {temp_min.text}ºC - {temp_max.text}ºC"
    elif temp_min is not None:
        return f"Minimum Temperature: {temp_min.text}ºC"
    elif temp_max is not None:
        return f"Maximum Temperature: {temp_max.text}ºC"
    return ""


def response_precipitation(node: ET.Element) -> str:
    """
    Returns the precipitaion forecast
    """
    rain_range = node.find(".//element[@type='precipitation_range']")
    precip_prob = node.find(".//text[@type='probability_of_precipitation']")
    if rain_range is not None and precip_prob is not None:
        return f"{precip_prob.text} Chance of Precipitation; {rain_range.text}"
    elif precip_prob is not None:
        return f"{precip_prob.text} Chance of Precipitation"
    return ""


def response_brisbane_detailed() -> Union[str, str, str]:
    """
    Returns a detailed forecast for Brisbane
    """
    try:
        data = urlopen("ftp://ftp.bom.gov.au/anon/gen/fwo/IDQ10605.xml")
        root = ET.fromstring(data.read())
    except Exception:
        return ""
    node = root.find(".//area[@description='Brisbane']")
    if node is None:
        return ""
    node = node.find(".//forecast-period[@index='0']")
    if node is None:
        return ""

    forecast = node.find(".//text[@type='forecast']")
    forecast = "" if forecast is None else forecast.text

    fire_danger = node.find(".//text[@type='fire_danger']")
    if fire_danger is None or fire_danger.text == "Low-Moderate":
        fire_danger = ""
    else:
        fire_danger = f"There Is A {fire_danger.text} Fire Danger Today"

    uv_alert = node.find(".//text[@type='uv_alert']")
    uv_alert = "" if uv_alert is None else uv_alert.text

    return (forecast, fire_danger, uv_alert)


@bot.on_command('weather')
def handle_weather(command: Command) -> None:
    """
    `!weather [[state] location] [day]` - Returns the weather forcaset for a location
    `day` is how many days into the future the forecast is for (0 is today and default)
    `location` defaults to Brisbane, and `state` defualts to QLD
    """

    (state, location, future) = process_arguments(command.arg)

    root = get_xml(state)
    if root is None:
        bot.post_message(command.channel_id, "Could Not Retrieve BOM Data")
        return

    node, response = find_location(root, location, future)
    if node is None:
        bot.post_message(command.channel_id, response)
        return

    # get responses
    response = []
    response.append(response_header(node, location))
    response.append(response_overall(node))
    response.append(response_temperature(node))
    response.append(response_precipitation(node))
    # post
    bot.post_message(command.channel_id, "\n".join([r for r in response if r]))


@bot.on_schedule('cron', hour=6, minute=0, timezone='Australia/Brisbane')
def daily_weather() -> None:
    """
    Posts today's Brisbane weather at 6:00am every day
    """

    (state, location, future) = ("QLD", "Brisbane", 0)

    root = get_xml(state)
    if root is None:
        return

    node, response = find_location(root, location, future)
    if node is None:
        return

    # get responses
    response = []
    brisbane_detailed, brisbane_fire, brisbane_uv = response_brisbane_detailed()
    response.append(response_header(node, location))
    response.append(response_overall(node))
    response.append(brisbane_detailed)
    response.append(response_temperature(node))
    response.append(brisbane_fire)
    response.append(brisbane_uv)
    # post
    general = bot.channels.get("general")
    bot.post_message(general.id, "\n".join([r for r in response if r]))
