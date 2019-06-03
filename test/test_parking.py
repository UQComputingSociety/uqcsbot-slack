from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
from unittest.mock import patch


def mocked_get_pf_parking_data():
    """
    Returns a local parking HTML document archived from the from UQ P&F website
    """
    try:
        data = open("test/parking.html").read()
    except Exception as e:
        raise e
        return None
    return data


@patch("uqcsbot.scripts.parking.get_pf_parking_data", new=mocked_get_pf_parking_data)
def test_parking(uqcsbot: MockUQCSBot):
    """
    Tests !parking
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!parking')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[-1]['text'] ==
            "*Available Parks at UQ St. Lucia*\n"
            "Few Carparks Availible in P1 - Warehouse (14P Daily)\n"
            "No Carparks Availible in P2 - Space Bank (14P Daily)\n"
            "No Carparks Availible in P6 - Hartley Teakle (14P Hourly)\n"
            "No Carparks Availible in P7 - DustBowl (14P Daily)\n"
            "Few Carparks Availible in P8 - Athletics Basement (14P Daily)\n"
            "No Carparks Availible in P8 - Athletics Roof (14P Daily)\n"
            "No Carparks Availible in P9 - Boatshed (14P Daily)\n"
            "204 Carparks Availible in P10 - UQ Centre & "
            "Playing Fields (14P Daily/14P Daily Capped)\n"
            "No Carparks Availible in P11 - Conifer Knoll Roof (14P Daily Restricted)")


@patch("uqcsbot.scripts.parking.get_pf_parking_data", new=mocked_get_pf_parking_data)
def test_parking_all(uqcsbot: MockUQCSBot):
    """
    Tests !parking all
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!parking all')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert (messages[-1]['text'] ==
            "*Available Parks at UQ St. Lucia*\n"
            "Few Carparks Availible in P1 - Warehouse (14P Daily)\n"
            "No Carparks Availible in P2 - Space Bank (14P Daily)\n"
            "266 Carparks Availible in P3 - Multi-Level West (Staff)\n"
            "115 Carparks Availible in P4 - Multi-Level East (Staff)\n"
            "No Carparks Availible in P6 - Hartley Teakle (14P Hourly)\n"
            "No Carparks Availible in P7 - DustBowl (14P Daily)\n"
            "Few Carparks Availible in P8 - Athletics Basement (14P Daily)\n"
            "No Carparks Availible in P8 - Athletics Roof (14P Daily)\n"
            "No Carparks Availible in P9 - Boatshed (14P Daily)\n"
            "204 Carparks Availible in P10 - UQ Centre & "
            "Playing Fields (14P Daily/14P Daily Capped)\n"
            "Few Carparks Availible in P11 - Conifer Knoll Lower (Staff)\n"
            "61 Carparks Availible in P11 - Conifer Knoll Upper (Staff)\n"
            "No Carparks Availible in P11 - Conifer Knoll Roof (14P Daily Restricted)")
