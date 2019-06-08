from test.conftest import MockUQCSBot, TEST_CHANNEL_ID
import pytest


def test_http(uqcsbot: MockUQCSBot):
    """
    Test !http.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!http 200')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == 'https://http.cat/200'


@pytest.mark.parametrize('code', ['', 'a', '1.0'])
def test_http_non_int(uqcsbot: MockUQCSBot, code: str):
    """
    Test !http with a non-integer.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, f'!http {code}')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == 'usage:  `!http <CODE>` - Returns a HTTP cat. '


def test_http_unavailable(uqcsbot: MockUQCSBot):
    """
    Test !http with an unavailable HTTP code.
    """
    uqcsbot.post_message(TEST_CHANNEL_ID, '!http 0')
    messages = uqcsbot.test_messages.get(TEST_CHANNEL_ID, [])
    assert len(messages) == 2
    assert messages[-1]['text'] == 'HTTP cat 0 is not available'
