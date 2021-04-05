import pytest


from test.conftest import MockUQCSBot


@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setenv("UQCSBOT_DB_URI", "sqlite:///:memory")
    monkeypatch.setattr(MockUQCSBot, "create_db_session", MockUQCSBot.mocked_create_db_session)

