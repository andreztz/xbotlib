"""XMPP bots for humans."""

from configparser import ConfigParser
from getpass import getpass
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
        return self.message["from"]

    @property
    def receiver(self):
        return self.message["to"]


class Bot(ClientXMPP):
    CONFIG_FILE = "bot.conf"

    def __init__(self):
        self.read_config()
        self.init_bot()
        self.register_xmpp_event_handlers()
        self.register_xmpp_plugins()
        self.run()

    def read_config(self):
        """Read configuration for running bot."""
        config_file_path = Path(self.CONFIG_FILE).absolute()

        if not exists(config_file_path):
            self.generate_config()

        self.config = ConfigParser()
        self.config.read(config_file_path)

    def generate_config(self):
        """Generate bot configuration."""
        jid = (
            input("XMPP address of your bot (e.g. alice@myserver.com): ")
            or "alice@myserver.com"
        )
        password = (
            getpass("Password for the bot account (e.g. my-cool-password): ")
            or "my-cool-password"
        )

        config = ConfigParser()
        config["bot"] = {"jid": jid, "password": password}

        with open("bot.conf", "w") as file_handle:
            config.write(file_handle)

    def init_bot(self):
        """Initialise bot with connection details."""
        jid = self.config["bot"]["jid"]
        passwd = self.config["bot"]["password"]
        ClientXMPP.__init__(self, jid, passwd)

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

    def groupchat_message(self, message):
        """Handle groupchat_message event."""
        pass

    def register_xmpp_plugins(self):
        """Register XMPP plugins that the bot supports."""
        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0045")  # Multi-User Chat
        self.register_plugin("xep_0199")  # XMPP Ping

    def run(self):
        """Run the bot."""
        self.connect()
        self.process()

    def reply(self, to, body, type="chat"):
        """Send a message."""
        self.send_message(mto=to, mbody=body, mtype=type)
