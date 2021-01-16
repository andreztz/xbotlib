"""XMPP bots for humans."""

import re
from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import datetime as dt
from getpass import getpass
from imghdr import what
from inspect import cleandoc
from logging import DEBUG, INFO, basicConfig, getLogger
from os import environ
from os.path import exists
from pathlib import Path
from random import choice
from sys import exit, stdout

from humanize import naturaldelta
from redis import Redis
from slixmpp import ClientXMPP


class SimpleMessage:
    """A simple message interface."""

    def __init__(self, message, bot):
        """Initialise the object."""
        self.message = message
        self.bot = bot

    @property
    def text(self):
        """The entire message text."""
        return self.message["body"]

    @property
    def content(self):
        """The content of the message received.

        This implementation aims to match and extract the content of the
        messages directed at bots in group chats. So, for example, when sending
        messages like so.

        echobot: hi
        echobot, hi
        echobot  hi

        The result produced by `message.content` will always be "hi". This
        makes it easier to work with various commands and avoid messy parsing
        logic in end-user implementations.
        """
        body = self.message["body"]

        try:
            match = f"^{self.bot.nick}.?(\s)"
            split = re.split(match, body)
            filtered = list(filter(None, split))
            return filtered[-1].strip()
        except Exception as exception:
            self.bot.log.error(f"Couldn't parse {body}: {exception}")
            return None

    @property
    def sender(self):
        """The sender of the message."""
        return self.message["from"]

    @property
    def room(self):
        """The room from which the message originated."""
        return self.message["from"].bare

    @property
    def receiver(self):
        """The receiver of the message."""
        return self.message["to"]

    @property
    def type(self):
        """The type of the message."""
        return self.message["type"]

    @property
    def nick(self):
        """The nick of the message."""
        return self.message["mucnick"]


class Config:
    """Bot file configuration."""

    def __init__(self, name, config):
        """Initialise the object."""
        self.name = name
        self.config = config
        self.section = config[self.name] if self.name in config else {}

    @property
    def account(self):
        """The account of the bot."""
        return self.section.get("account", None)

    @property
    def password(self):
        """The password of the bot account."""
        return self.section.get("password", None)

    @property
    def nick(self):
        """The nickname of the bot."""
        return self.section.get("nick", None)


class Bot(ClientXMPP):
    """XMPP bots for humans."""

    DIRECT_MESSAGE_TYPES = ("chat", "normal")
    GROUP_MESSAGE_TYPES = ("groupchat", "normal")

    def __init__(self):
        """Initialise the object."""
        self.name = type(self).__name__.lower()
        self.start = dt.now()

        self.CONFIG_FILE = f"{self.name}.conf"

        self.parse_arguments()
        self.setup_logging()
        self.read_config()
        self.init_bot()
        self.register_xmpp_event_handlers()
        self.register_xmpp_plugins()
        self.init_db()
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
        message = SimpleMessage(message, self)
        self.log.error(f"Received error message: {message.text}")

    def direct_message(self, message):
        """Handle direct message events."""
        message = SimpleMessage(message, self)

        if message.type not in self.DIRECT_MESSAGE_TYPES:
            return

        if message.text.startswith("@"):
            self.command(message, to=message.sender)

        try:
            self.direct(message)
        except AttributeError:
            self.log.info(f"Bot.direct not implemented for {self.nick}")

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
        """Handle group chat message events."""
        message = SimpleMessage(message, self)

        if message.text.startswith("@"):
            return self.meta(message, room=message.room)

        miss = message.type not in self.GROUP_MESSAGE_TYPES
        loop = message.nick == self.nick
        other = self.nick not in message.text

        if miss or loop or other:
            return

        if message.content.startswith("@"):
            self.command(message, room=message.room)

        try:
            self.group(message)
        except AttributeError:
            self.log.info(f"Bot.group not implemented for {self.nick}")

    def register_xmpp_plugins(self):
        """Register XMPP plugins that the bot supports."""
        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0045")  # Multi-User Chat
        self.register_plugin("xep_0199")  # XMPP Ping
        self.register_plugin("xep_0084")  # User Avatar

    def init_db(self):
        """Initialise the Redis key/value store."""
        url = environ.get("REDIS_URL", None)

        if not url:
            self.db = None
            self.log.info("No storage discovered")
        else:
            self.db = Redis.from_url(url, decode_responses=True)
            self.log.info("Successfully connected to storage")

    def run(self):
        """Run the bot."""
        self.connect()

        try:
            self.process()
        except KeyboardInterrupt:
            pass

    def reply(self, text, to=None, room=None):
        """Send back a reply."""
        if to is None and room is None:
            self.log.error("`to` or `room` arguments required for `reply`")
            exit(1)

        if to is not None and room is not None:
            self.log.error("Cannot send to both `to` and `room` for `reply`")
            exit(1)

        kwargs = {"mbody": text}
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

    def meta(self, message, **kwargs):
        """Handle meta command invocations."""
        if message.text.startswith("@bots"):
            self.reply("🖐️", **kwargs)

    def command(self, message, **kwargs):
        """Handle command invocations."""
        if message.content.startswith("@uptime"):
            self.reply(self.uptime, **kwargs)
        elif message.content.startswith("@help"):
            try:
                self.reply(cleandoc(self.help), **kwargs)
            except AttributeError:
                self.reply("No help found 🤔️", **kwargs)


class EchoBot(Bot):
    """Responds with whatever you send.

    Simply direct message the bot and see if you get back what you sent. It
    also works in group chats but in this case you need to summon the bot using
    its nickname.
    """

    help = "I echo messages back 🖖️"

    def direct(self, message):
        """Send back whatever we receive."""
        self.reply(message.text, to=message.sender)

    def group(self, message):
        """Send back whatever receive in group chats."""
        self.reply(message.content, room=message.room)


class WhisperBot(Bot):
    """Anonymous whispering in group chats.

    In order to activate this bot you can invite it to your group chat. Once
    invited, you can start a private chat with the bot and tell it you want it
    to whisper your message into the group chat. The bot will then do this on
    your behalf and not reveal your identity. This is nice when you want to
    communicate with the group anonymously.
    """

    help = "I whisper private messages into group chats 😌️"

    def direct(self, message):
        """Receive private messages and whisper them into group chats."""
        self.reply(f"*pssttt...* {message.content}", room=message.room)


class GlossBot(Bot):
    """Building a shared glossary together.

    A glossary is "an alphabetical list of terms in a particular domain of
    knowledge with the definitions for those terms."

    This bot reacts to commands which insert, list or delete items from a
    shared glossary when summoned in a group chat. This bot makes use of
    persistent storage so the glossary is always there even if the bot goes
    away.
    """

    help = """
    I help build a shared glossary
      glossbot: @add <entry> - <definition>
      glossbot: @rm <entry>
      glossbot: @rand
      glossbot: @ls
    """

    def group(self, message):
        """Handle glossary commands."""
        if "@add" in message.content:
            try:
                parsed = self.parse_add(message)
                self.add(*parsed, room=message.room)
            except Exception:
                response = f"Couldn't understand '{message.content}'?"
                self.reply(response, room=message.sender)
        elif "@rm" in message.content:
            try:
                parsed = message.content.split("@rm")[-1].strip()
                self.rm(parsed, room=message.room)
            except Exception:
                response = f"Couldn't understand '{message.content}'?"
                self.reply(response, room=message.sender)
        elif "@rand" in message.content:
            self.rand(room=message.room)
        elif "@ls" in message.content:
            self.ls(room=message.room)
        else:
            self.log.info(f"{message.text} not recognised as glossbot command")

    def parse_add(self, message):
        """Parse the add command syntax."""
        try:
            replaced = message.content.replace("@add", "")
            return [s.strip() for s in replaced.split("-")]
        except ValueError:
            self.log.error(f"Failed to parse {message.content}")

    def add(self, entry, definition, **kwargs):
        """Add a new entry."""
        self.db[entry] = definition
        self.reply("Added ✌️", **kwargs)

    def rand(self, **kwargs):
        """List a random entry."""
        if not self.db.keys():
            return self.reply("Glossary is empty 🙃️", **kwargs)

        entry = choice(self.db.keys())
        self.reply(f"{entry} - {self.db[entry]}", **kwargs)

    def ls(self, **kwargs):
        """List all entries."""
        if not self.db.keys():
            return self.reply("Glossary is empty 🙃️", **kwargs)

        for entry in sorted(self.db.keys()):
            self.reply(f"{entry} - {self.db[entry]}", **kwargs)

    def rm(self, entry, **kwargs):
        """Remove an entry."""
        if entry not in self.db.keys():
            return self.reply(f"{entry} doesn't exist?", **kwargs)

        self.db.delete(entry)
        self.reply("Removed ✌️", **kwargs)
