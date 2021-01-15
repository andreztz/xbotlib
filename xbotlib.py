"""XMPP bots for humans."""

from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime as dt
from getpass import getpass
from imghdr import what
from logging import DEBUG, INFO, basicConfig, getLogger
from os import environ
from os.path import exists
from pathlib import Path
from sys import exit, stdout

from humanize import naturaldelta
from slixmpp import ClientXMPP


class SimpleMessage:
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
    def room(self):
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


class Config:
    """Bot file configuration."""

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.section = config[self.name] if self.name in config else {}

    @property
    def account(self):
        return self.section.get("account", None)

    @property
    def password(self):
        return self.section.get("password", None)

    @property
    def nick(self):
        return self.section.get("nick", None)


class Bot(ClientXMPP):
    """XMPP bots for humans."""

    def __init__(self):
        self.name = type(self).__name__.lower()
        self.start = dt.now()

        self.CONFIG_FILE = f"{self.name}.conf"

        self.parse_arguments()
        self.setup_logging()
        self.read_config()
        self.init_bot()
        self.register_xmpp_event_handlers()
        self.register_xmpp_plugins()
        self.run()

    def parse_arguments(self):
        """Parse command-line arguments."""
        self.parser = ArgumentParser(description="XMPP bots for humans")

        self.parser.add_argument(
            "-d",
            "--debug",
            help="Enable verbose debug logs",
            action="store_const",
            dest="log_level",
            const=DEBUG,
            default=INFO,
        )
        self.parser.add_argument(
            "-a",
            "--account",
            dest="account",
            help="Account for the bot account (foo@example.com)",
        )
        self.parser.add_argument(
            "-p",
            "--password",
            dest="password",
            help="Password for the bot account",
        )
        self.parser.add_argument(
            "-n",
            "--nick",
            dest="nick",
            help="Nickname for the bot account",
        )
        self.parser.add_argument(
            "-av",
            "--avatar",
            dest="avatar",
            help="Avatar for the bot account",
            default="avatar.png",
        )

        self.args = self.parser.parse_args()

    def setup_logging(self):
        """Arrange logging for the bot."""
        basicConfig(
            level=self.args.log_level, format="%(levelname)-8s %(message)s"
        )
        self.log = getLogger(__name__)

    def read_config(self):
        """Read configuration for running bot."""
        config = ConfigParser()

        config_file_path = Path(self.CONFIG_FILE).absolute()

        if not exists(config_file_path) and stdout.isatty():
            self.log.info(f"Did not find {config_file_path}")
            self.generate_config_interactively()

        if exists(config_file_path):
            config.read(config_file_path)

        self.config = Config(self.name, config)

    def generate_config_interactively(self):
        """Generate bot configuration."""
        account = input("Account: ")
        password = getpass("Password: ")
        nick = input("Nickname: ")

        config = ConfigParser()
        config[self.name] = {"account": account, "password": password}

        if nick:
            config[self.name]["nick"] = nick

        with open(self.CONFIG_FILE, "w") as file_handle:
            config.write(file_handle)

    def init_bot(self):
        """Initialise bot with connection details."""
        account = (
            self.args.account
            or self.config.account
            or environ.get("XBOT_ACCOUNT", None)
        )
        password = (
            self.args.password
            or self.config.password
            or environ.get("XBOT_PASSWORD", None)
        )
        nick = (
            self.args.nick or self.config.nick or environ.get("XBOT_NICK", None)
        )

        if not account:
            self.log.error("Unable to discover account")
            exit(1)
        if not password:
            self.log.error("Unable to discover password")
            exit(1)
        if not nick:
            self.log.error("Unable to discover nick")
            exit(1)

        ClientXMPP.__init__(self, account, password)

        self.account = account
        self.password = password
        self.nick = nick

        self.avatar = self.args.avatar

    def register_xmpp_event_handlers(self):
        """Register functions against specific XMPP event handlers."""
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_invite", self.group_invite)
        self.add_event_handler("message", self.direct_message)
        self.add_event_handler("groupchat_message", self.group_message)
        self.add_event_handler("message_error", self.error_message)

    def error_message(self, message):
        _message = SimpleMessage(message)
        self.log.error(f"Received error message: {_message.body}")

    def direct_message(self, message):
        """Handle message event."""
        if message["type"] in ("chat", "normal"):
            _message = SimpleMessage(message)

            if _message.body.startswith("!"):
                self.command(_message, to=_message.sender)
                return

            try:
                self.direct(_message)
            except AttributeError:
                self.log.info("Bot.direct not implemented")

    def session_start(self, message):
        """Handle session_start event."""
        self.send_presence()
        self.get_roster()
        self.publish_avatar()

    def publish_avatar(self):
        """Publish bot avatar."""
        try:
            abspath = Path(self.avatar).absolute()
            with open(abspath, "rb") as handle:
                contents = handle.read()
        except IOError:
            self.log.info(f"No avatar discovered (tried '{abspath}')")
            return

        id = self.plugin["xep_0084"].generate_id(contents)
        info = {
            "id": id,
            "type": f"image/{what('', contents)}",
            "bytes": len(contents),
        }

        self.plugin["xep_0084"].publish_avatar(contents)
        self.plugin["xep_0084"].publish_avatar_metadata(items=[info])

    def group_invite(self, message):
        """Accept invites to group chats."""
        self.plugin["xep_0045"].join_muc(message["from"], self.config.nick)

    def group_message(self, message):
        """Handle groupchat_message event."""
        if message["type"] in ("groupchat", "normal"):
            if message["mucnick"] != self.config.nick:
                _message = SimpleMessage(message)

                if f"{self.nick}:!" in _message.body:
                    self.command(_message, room=_message.room)
                    return

                try:
                    self.group(_message)
                except AttributeError:
                    self.log.info("Bot.group not implemented")

    def register_xmpp_plugins(self):
        """Register XMPP plugins that the bot supports."""
        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0045")  # Multi-User Chat
        self.register_plugin("xep_0199")  # XMPP Ping
        self.register_plugin("xep_0084")  # User Avatar

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
            self.log("`to` or `room` arguments required for `reply`")
            exit(1)

        if to is not None and room is not None:
            self.log.error("Cannot send to both `to` and `room` for `reply`")
            exit(1)

        kwargs = {"mbody": body}
        if to is not None:
            kwargs["mto"] = to
            kwargs["mtype"] = "chat"
        else:
            kwargs["mto"] = room
            kwargs["mtype"] = "groupchat"

        self.send_message(**kwargs)

    @property
    def uptime(self):
        """Time since the bot came up."""
        return naturaldelta(self.start - dt.now())

    def command(self, message, **kwargs):
        """Handle "!" style commands with built-in responses."""
        command = message.body.split("!")[-1]

        if command == "uptime":
            self.reply(self.uptime, **kwargs)
        elif command == "help":
            try:
                self.reply(self.help, **kwargs)
            except AttributeError:
                self.reply("No help found 🤔️", **kwargs)
        elif command == "bots" and "room" in kwargs:
            self.reply("o/", **kwargs)
        else:
            self.log.error(f"'{command}' command is not recognised")


class EchoBot(Bot):
    """Responds with whatever you send.

    Simply direct message the bot and see if you get back what you sent. It
    also works in group chats but in this case you need to summon the bot using
    its nickname. Usually like so.

    echobot:foo

    """

    help = "I echo back whatever you send to me 🖖️"

    def direct(self, message):
        """Send back whatever we receive."""
        self.reply(message.body, to=message.sender)

    def group(self, message):
        """Send back whatever receive in group chats."""
        if "echobot" in message.body:
            self.reply(message.body.split(":")[-1], room=message.room)


class WhisperBot(Bot):
    """Anonymous whispering in group chats.

    In order to activate this bot you can invite it to your group chat. Once
    invited, you can start a private chat with the bot and tell it you want it
    to whisper your message into the group chat. The bot will then do this on
    your behalf and not reveal your identity. This is nice when you want to
    communicate with the group anonymously.

    """

    help = "I whisper your private messages into group chats 😌️"

    def direct(self, message):
        """Receive private messages and whisper them into group chats."""
        self.reply(f"*pssttt...* {message.body}", room=message.room)
