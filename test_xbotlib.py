"""Unit tests for xbotlib module."""

from logging import getLogger

from pytest import fixture

from xbotlib import Config, SimpleDatabase, SimpleMessage

log = getLogger(__name__)


@fixture
def message():
    class MockFrom:
        @property
        def bare(self):
            return "foo@muc.vvvvvvaria.org"

    return {
        "body": "mockbot: foobar",
        "from": MockFrom(),
        "to": "other_tester",
        "type": "chat",
        "mucnick": "mockbot",
        "oob": {"url": "https://foo.com"},
    }


@fixture
def bot():
    class MockBot:
        @property
        def nick(self):
            return "mockbot"

        @property
        def log(self):
            raise NotImplementedError()

    return MockBot()


@fixture
def config():
    return Config(
        "test",
        {
            "test": {
                "account": "foo@vvvvvvaria.org",
                "password": "SecretPasswordZ",
                "nick": "foo",
                "avatar": "avatar.png",
                "redis_url": "redis://localhost:6379/0",
                "rooms": "foo, bar, baz",
                "no_auto_join": True,
                "port": 8080,
                "template": "index.html.j2",
                "serve": True,
                "storage": "file",
                "output": ".",
            }
        },
    )


@fixture
def tmp_db_path(tmp_path):
    return tmp_path / "testbot.json"


def test_simple_message(message):
    sm = SimpleMessage(message, "mockbot", log)
    assert sm.message == message
    assert sm.text == "mockbot: foobar"
    assert sm.content == "foobar"
    # TODO*decentral1se): how to test test this?
    # assert sm.sender == "tester"
    assert sm.room == "foo@muc.vvvvvvaria.org"
    assert sm.receiver == "other_tester"
    assert sm.type == "chat"
    assert sm.nick == "mockbot"
    assert sm.url == "https://foo.com"


def test_empty_config():
    config = Config("test", {})
    assert config.account is None


def test_config(config):
    assert config.account == "foo@vvvvvvaria.org"
    assert config.password == "SecretPasswordZ"
    assert config.nick == "foo"
    assert config.avatar == "avatar.png"
    assert config.redis_url == "redis://localhost:6379/0"
    assert config.rooms == ["foo", "bar", "baz"]
    assert config.no_auto_join
    assert config.port == 8080
    assert config.template == "index.html.j2"
    assert config.serve
    assert config.storage == "file"
    assert config.output == "."


def test_simple_message_delete(tmp_db_path):
    db = SimpleDatabase(tmp_db_path, log)
    db["foo"] = "bar"
    del db["foo"]
    assert "foo" not in db
