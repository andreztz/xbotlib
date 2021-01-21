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
from sys import exit, stdout

from aiohttp.web import Application, Response, get, run_app
from humanize import naturaldelta
from jinja2 import Environment, FileSystemLoader
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
            match = fr"^{self.bot.nick}.?(\s)"
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

    @property
    def url(self):
        """The URL of a sent file."""
        return self.message["oob"]["url"]


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

    @property
    def avatar(self):
        """The avatar of the bot."""
        return self.section.get("avatar", None)

    @property
    def redis_url(self):
        """The Redis connection URL."""
        return self.section.get("redis_url", None)

    @property
    def rooms(self):
        """A list of rooms to automatically join."""
        rooms = self.section.get("rooms", None)

        if rooms is None:
            return None

        return [room.strip() for room in rooms.split(",")]

    @property
    def no_auto_join(self):
        """Disable auto-join when invited."""
        return self.section.get("no_auto_join", None)

    @property
    def port(self):
        """The port to serve from."""
        return self.section.get("port", None)

    @property
    def template(self):
        """The Jinja template to render."""
        return self.section.get("template", None)


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
            help="Account for the bot account",
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
            "-av", "--avatar", dest="avatar", help="Avatar for the bot account"
        )
        self.parser.add_argument(
            "-ru",
            "--redis-url",
            dest="redis_url",
            help="Redis storage connection URL",
        )
        self.parser.add_argument(
            "-r",
            "--rooms",
            dest="rooms",
            nargs="+",
            help="Rooms to automatically join",
        )
        self.parser.add_argument(
            "--no-auto-join",
            default=False,
            action="store_true",
            dest="no_auto_join",
            help="Disable automatically joining rooms when invited",
        )
        self.parser.add_argument(
            "-pt",
            "--port",
            dest="port",
            help="The port to serve from",
        )
        self.parser.add_argument(
            "-t",
            "--template",
            dest="template",
            help="The template to render",
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
        print("*" * 79)
        print(
            "Please enter the XMPP user account of your bot. ",
            "This is often referred to as the JID (Jabbed ID). ",
            "An example would be echobot@vvvvvvaria.org",
            sep="\n",
        )
        account = input("Account: ")

        print("Please enter the password for your bot account")
        password = getpass("Password: ")
        print("*" * 79)

        config = ConfigParser()
        config[self.name] = {"account": account, "password": password}

        with open(self.CONFIG_FILE, "w") as file_handle:
            config.write(file_handle)
            self.log.info(f"Generated {self.CONFIG_FILE}")

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
        avatar = (
            self.args.avatar
            or self.config.avatar
            or environ.get("XBOT_AVATAR", None)
            or "avatar.png"
        )
        redis_url = (
            self.args.redis_url
            or self.config.redis_url
            or environ.get("XBOT_REDIS_URL", None)
        )
        rooms = (
            self.args.rooms
            or self.config.rooms
            or environ.get("XBOT_ROOMS", None)
        )
        no_auto_join = (
            self.args.no_auto_join
            or self.config.no_auto_join
            or environ.get("XBOT_NO_AUTO_JOIN", None)
        )
        port = (
            self.args.port
            or self.config.port
            or environ.get("XBOT_PORT", None)
            or "8080"
        )
        template = (
            self.args.template
            or self.config.template
            or environ.get("XBOT_TEMPLATE", None)
            or "index.html.j2"
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
        self.avatar = avatar
        self.redis_url = redis_url
        self.rooms = rooms
        self.no_auto_join = no_auto_join
        self.port = port
        self.template = self.load_template(template)

    def load_template(self, template):
        """Load template via Jinja."""
        if not exists(Path(template).absolute()):
            return None

        try:
            loader = FileSystemLoader(searchpath="./")
            env = Environment(loader=loader)
            return env.get_template(template)
        except Exception:
            self.log.info(f"Unable to load {template}")

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
            if self.command(message, to=message.sender):
                return

        try:
            self.direct(message)
        except AttributeError:
            self.log.info(f"Bot.direct not implemented for {self.nick}")

    def session_start(self, message):
        """Handle session_start event."""
        self.send_presence()
        self.get_roster()
        self.publish_avatar()
        self.join_rooms()

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

    def join_rooms(self):
        """Automatically join rooms if specified."""
        if self.rooms is None:
            return

        for room in self.rooms:
            self.plugin["xep_0045"].join_muc(room, self.config.nick)
            self.log.info(f"Joining {room} automatically")

    def group_invite(self, message):
        """Accept invites to group chats."""
        room = message["from"]

        if self.no_auto_join:
            return self.log.info(f"Not joining {room} (disabled)")

        self.plugin["xep_0045"].join_muc(room, self.config.nick)
        self.log.info(f"Joining {room} as invited")

    def group_message(self, message):
        """Handle group chat message events."""
        message = SimpleMessage(message, self)

        if "@" in message.text:
            if self.meta(message, room=message.room):
                return

        miss = message.type not in self.GROUP_MESSAGE_TYPES
        loop = message.nick == self.nick
        other = self.nick not in message.text and not message.url

        if miss or other or loop:
            return

        if "@" in message.content:
            if self.command(message, room=message.room):
                return

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
        self.register_plugin("xep_0066")  # Proces URIs (files, images)

        try:
            for plugin in self.plugins:
                self.register_plugin(plugin)
                self.log.info(f"Loaded {plugin}")
        except AttributeError:
            self.log.info("No additional plugins loaded")

    def init_db(self):
        """Initialise the Redis key/value store."""
        if not self.redis_url:
            self.db = None
            return self.log.info("No Redis storage discovered")

        try:
            self.db = Redis.from_url(self.redis_url, decode_responses=True)
            self.log.info("Successfully connected to Redis storage")
        except ValueError:
            self.log.info("Failed to connect to Redis storage")

    def run(self):
        """Run the bot."""
        self.connect()

        try:
            self.serve_web()
            self.process(forever=False)
        except (KeyboardInterrupt, RuntimeError):
            pass

    def serve_web(self):
        """Serve the web."""
        self.web = Application()

        try:
            self.web.add_routes([get("/", self.serve)])
        except AttributeError:
            self.web.add_routes([get("/", self.default_serve)])

        self.log.info(f"Serving on http://0.0.0.0:{self.port}")
        run_app(self.web, port=self.port, print=None)

    async def default_serve(self, request):
        """Default placeholder text for HTML serving."""
        return Response(text=f"{self.nick} is alive and well")

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
        return True

    @property
    def uptime(self):
        """Time since the bot came up."""
        return naturaldelta(self.start - dt.now())

    def meta(self, message, **kwargs):
        """Handle meta command invocations."""
        if "@bots" in message.text:
            return self.reply("🖐️", **kwargs)

    def command(self, message, **kwargs):
        """Handle command invocations."""
        if "@uptime" in message.content:
            return self.reply(self.uptime, **kwargs)
        elif "@help" in message.content:
            try:
                return self.reply(cleandoc(self.help), **kwargs)
            except AttributeError:
                return self.reply("No help found 🤔️", **kwargs)

    def respond(self, response, content_type="text/html"):
        """Send this response back with the web server."""
        return Response(text=response, content_type=content_type)
