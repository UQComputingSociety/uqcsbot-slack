from test.conftest import MockUQCSBot, TEST_CHANNEL_ID


def test_meme(uqcsbot: MockUQCSBot):
    """
    Test !meme
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!meme bender "top" "bottom"')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])

    assert len(messages) == 2
    image_url = messages[-1]['attachments'][0]['image_url']
    assert image_url == 'https://memegen.link/bender/top/bottom.jpg'
