"""XMPP bots for humans."""

from argparse import ArgumentParser, BooleanOptionalAction
from configparser import ConfigParser
from getpass import getpass
from os import environ
from os.path import exists
from pathlib import Path

from slixmpp import ClientXMPP


class EasyMessage:
    """A simple message interface."""

    def __init__(self, message):
        self.message = message

    @property
    def body(self):
        return self.message["body"]

    @property
    def sender(self):
        return self.message["from"].bare

    @property
    def receiver(self):
        return self.message["to"]

    @property
    def nickname(self):
        return self.message["mucnick"]

    @property
    def type(self):
        return self.message["type"]


class Bot(ClientXMPP):
    CONFIG_FILE = "bot.conf"

    def __init__(self):
        self.parse_arguments()
        self.read_config()
        self.init_bot()
        self.register_xmpp_event_handlers()
        self.register_xmpp_plugins()
        self.run()

    def parse_arguments(self):
        """Parse command-line arguments."""
        self.parser = ArgumentParser()
        self.parser.add_argument(
            "--input",
            help="Read configuration from environment",
            action=BooleanOptionalAction,
            default=True,
        )
        self.args = self.parser.parse_args()

    def read_config(self):
        """Read configuration for running bot."""
        self.config = ConfigParser()

        config_file_path = Path(self.CONFIG_FILE).absolute()
        if not exists(config_file_path) and self.args.input:
            self.generate_config_interactively()

        if exists(config_file_path):
            self.config.read(config_file_path)

        if self.args.input is False:
            self.read_config_from_env()

        if "bot" not in self.config:
            raise RuntimeError("Failed to configure bot")

    def generate_config_interactively(self):
        """Generate bot configuration."""
        jid = input("XMPP address (e.g. foo@bar.com): ") or "foo@bar.com"
        password = (
            getpass("Password (e.g. my-cool-password): ") or "my-cool-password"
        )
        room = input("XMPP room (e.g. foo@muc.bar.com): ")
        nick = input("Nickname (e.g. lurkbot): ")

        config = ConfigParser()
        config["bot"] = {"jid": jid, "password": password}

        if room:
            config["bot"]["room"] = room
        if nick:
            config["bot"]["nick"] = nick

        with open("bot.conf", "w") as file_handle:
            config.write(file_handle)

    def read_config_from_env(self):
        """Read configuration from the environment."""
        self.config["bot"] = {}
        self.config["bot"]["jid"] = environ.get("XBOT_JID")
        self.config["bot"]["password"] = environ.get("XBOT_PASSWORD")
        self.config["bot"]["room"] = environ.get("XBOT_ROOM")
        self.config["bot"]["nick"] = environ.get("XBOT_NICK")

    def init_bot(self):
        """Initialise bot with connection details."""
        jid = self.config["bot"]["jid"]
        password = self.config["bot"]["password"]
        ClientXMPP.__init__(self, jid, password)

    def register_xmpp_event_handlers(self):
        """Register functions against specific XMPP event handlers."""
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("groupchat_message", self.groupchat_message)

    def message(self, message):
        """Handle message event."""
        if message["type"] in ("chat", "normal"):
            self.react(EasyMessage(message))

    def session_start(self, event):
        """Handle session_start event."""
        self.send_presence()
        self.get_roster()

        room = self.config["bot"].get("room")
        nick = self.config["bot"].get("nick")

        if room and nick:
            self.plugin["xep_0045"].join_muc(room, nick)

    def groupchat_message(self, message):
        """Handle groupchat_message event."""
        if message["type"] in ("groupchat", "normal"):
            if message["mucnick"] != self.config["bot"]["nick"]:
                self.react(EasyMessage(message))

    def register_xmpp_plugins(self):
        """Register XMPP plugins that the bot supports."""
        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0045")  # Multi-User Chat
        self.register_plugin("xep_0199")  # XMPP Ping

    def run(self):
        """Run the bot."""
        self.connect()

        try:
            self.process()
        except KeyboardInterrupt:
            pass

    def reply(self, body, to=None, room=None):
        """Send back a reply."""
        if to is None and room is None:
            message = "`to` or `room` arguments required for `reply`"
            raise RuntimeError(message)

        if to is not None and room is not None:
            message = "Cannot send to both `to` and `room` for `reply`"
            raise RuntimeError(message)

        kwargs = {"mbody": body}
        if to is not None:
            kwargs["mto"] = to
            kwargs["mtype"] = "chat"
        else:
            kwargs["mto"] = room
            kwargs["mtype"] = "groupchat"

        self.send_message(**kwargs)

    def react(self, message):
        message = "You need to write your own `react` implementation"
        raise NotImplementedError(message)
