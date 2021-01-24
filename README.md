# xbotlib

[![PyPI version](https://badge.fury.io/py/xbotlib.svg)](https://badge.fury.io/py/xbotlib)
[![Build Status](https://drone.autonomic.zone/api/badges/decentral1se/xbotlib/status.svg?ref=refs/heads/main)](https://drone.autonomic.zone/decentral1se/xbotlib)

## XMPP bots for humans

> status: experimental

A friendly lightweight wrapper around
[slixmpp](https://slixmpp.readthedocs.io/) for writing XMPP bots in Python. The
goal is to make writing and running XMPP bots easy and fun. `xbotlib` is a
[single file implementation](./xbotlib.py) which can easily be understood and
extended. The `xbotlib` source code and ideas are largely borrowed from the
XMPP bot experiments going on in
[Varia](https://git.vvvvvvaria.org/explore/repos?tab=&sort=recentupdate&q=bots).

- [Install](#install)
- [Getting Started](#getting-started)
- [Working with your bot](#working-with-your-bot)
  - [Documentation](#documentation)
  - [Commands](#commands)
  - [Avatars](#avatars)
  - [Configuration](#configuration)
    - [Using the `.conf` configuration file](#using-the--conf--configuration-file)
    - [Using the command-line interface](#using-the-command-line-interface)
    - [Using the environment](#using-the-environment)
  - [Storage back-end](#storage-back-end)
  - [Loading Plugins](#loading-plugins)
  - [Serving HTTP](#serving-http)
  - [API Reference](#api-reference)
    - [Bot.direct(message)](#botdirect-message-)
    - [Bot.group(message)](#botgroup-message-)
    - [Bot.serve(request)](#botserve-request-)
  - [Bot.routes()](#botroutes--)
    - [Bot.setup()](#botsetup--)
    - [SimpleMessage](#simplemessage)
    - [Bot](#bot)
- [Chatroom](#chatroom)
- [More Examples](#more-examples)
- [Deploy your bots](#deploy-your-bots)
- [Roadmap](#roadmap)
- [Changes](#changes)
- [License](#license)

## Install

```sh
$ pip install xbotlib
```

## Getting Started

Put the following in a `echo.py` file. This bot echoes back whatever message
you send it in both direct messages and group messages. In group chats, you
need to message the bot directly (e.g. `echobot: hi`) (see [the commands
section](#commands) for more).

```python
from xbotlib import Bot

class EchoBot(Bot):
    def direct(self, message):
        self.reply(message.text, to=message.sender)

    def group(self, message):
        self.reply(message.content, room=message.room)

EchoBot()
```

And then `python echo.py`. You will be asked a few questions in order to load
the account details that your bot will be using. This will generate an
`echobot.conf` file in the same working directory for further use. See the
[configuration](#configure-your-bot) section for more.

That's it! If you want to go further, continue reading [here](#working-with-your-bot).

## Working with your bot

The following sections try to cover all the ways you can configure and extend
your bot using `xbotlib`. If anything is unclear, please let us know [on the
chat](#chatroom).

### Documentation

Add a `help = "my help"` to your `Bot` class like so.

```python
class MyBot(Bot):
    help = """This is my cool help.

    I can list some commands too:

      @foo - some command
    """
```

Your bot will then respond to `mybot: @help` invocations. This string can be a
multi-line string with indentation. `xbotlib` will try to format this sensibly
for showing in chat clients.

See more in the [commands](#commands) section for more.

### Commands

Using `@<command>` in direct messages and `<nick>, @<command>` (the `,` is
optional, anything will be accepted here and there doesn't seem to be a
consensus on what is most common way to "at" another user in XMPP) in group chats,
here are the supported commands.

- `@uptime`: how long the bot has been running
- `@help`: the help text for what the bot does

There are also more general status commands which all bots respond to.

- `@bots`: status check on who is a bot in the group chat

These commands will be detected in any part of the message sent to the bot. So
you can write `echobot, can we see your @uptime`, or `I'd love to know which @bots are here.`

### Avatars

By default, `xbotlib` will look for an `avatar.png` (so far tested with `.png`
but other file types may work) file alongside your Python script which contains
your bot implementation. You can also specify another path using the `--avatar`
option on the command-line interface. The images should ideally have a height
of `64` and a width of `64` pixels each.

### Configuration

All the ways you can pass configuration details to your bot. There are three
ways to configure your bot, the configuration file, command-line interface and
the environment. Use whichever one suits you best. The values are loaded in the
following order: command-line > configuration file > environment. This means
you can override everything from the command-line easily.

#### Using the `.conf` configuration file

If you run simply run your Python script which contains the bot then `xbotlib`
will generate a configuration for you by asking a few questions. This is the
simplest way to run your bot locally.

- **account**: the account of the bot
- **password**: the password of the bot account
- **nick**: the nickname of the bot
- **avatar**: the avatar of the bot (default: `avatar.png`)
- **redis_url**: the Redis connection URL
- **rooms**: a list of rooms to automatically join
- **no_auto_join**: disable auto-join when invited (default: `False`)
- **template**: the port to serve from (default: `index.html.j2`)
- **serve**: turn on the web server (default: `False`)
- **port**: the port to serve from (default: `8080`)
- **storage**: storage back-end (default: `file`)
- **storage_file**: path to file based storage back-end (default: `<nick>.json>`)

#### Using the command-line interface

Every bot accepts a number of comand-line arguments to load configuration. You
can use the `--help` option to see what is available (e.g. `python bot.py --help`).

- **-h, --help**: show this help message and exit
- **-d, --debug**: enable verbose debug logs
- **-a ACCOUNT, --account ACCOUNT**: account for the bot account
- **-p PASSWORD, --password PASSWORD**: password for the bot account
- **-n NICK, --nick NICK**: nickname for the bot account
- **-av AVATAR, --avatar AVATAR**: avatar for the bot account (default: `avatar.png`)
- **-ru REDIS_URL, --redis-url REDIS_URL**: redis storage connection URL
- **-r ROOMS [ROOMS ...], --rooms ROOMS [ROOMS ...]**: Rooms to automatically join
- **-naj, --no-auto-join**: disable automatically joining rooms when invited (default: `False`)
- **-pt PORT, --port PORT**: the port to serve from (default: `8080`)
- **-t TEMPLATE, --template TEMPLATE**: the template to render (default: `index.html.j2`)
- **-s, --serve**: turn on the web server (default: `False`)
- **-st {file,redis}, --storage {file,redis}**: choice of storage back-end (default: `file`)
- **-stf STORAGE_FILE, --storage-file STORAGE_FILE**: path to file based storage back-end (default: `<nick>.json`)

#### Using the environment

`xbotlib` will try to read the following configuration values from the
environment if it cannot read them from a configuration file or the
command-line interface. This can be useful when doing remote server
deployments.

- **XBOT_ACCOUNT**: The bot account
- **XBOT_PASSWORD**: The bot password
- **XBOT_NICK**: The bot nickname
- **XBOT_AVATAR**: The bot avatar icon (default: `avatar.png`)
- **XBOT_REDIS_URL**: Redis key store connection URL
- **XBOT_ROOMS**: The rooms to automatically join
- **XBOT_NO_AUTO_JOIN**: Disable auto-joining on invite (default: `False`)
- **XBOT_TEMPLATE**: the template to render (default: `index.html.j2`)
- **XBOT_SERVE**: Turn on the web server (default: `False`)
- **XBOT_PORT**: The port to serve from (default: `8080`)
- **XBOT_STORAGE**: choice of storage back-end (default: `file`)
- **XBOT_STORAGE_FILE**: path to file based storage back-end (default: `<nick>.json`)

### Storage back-end

In order to store data you can make use of the `self.db` attribute of the `Bot`
class. It is a Python dictionary which will be saved to disk automatically for
you as a `<nick>.json` in your current working directory. The name and path to
this file can be configured using the storage file option.

```python
def group(self, message):
    if not message.room in self.db.keys():
        self.db[message.room] = "visited"
```

If you want to inspect the database when the bot is not running, you can look
in the file directly.

```bash
$ cat <nick>.json
```

For more advanced use cases, `xbotlib` also supports [Redis](https://redis.io/)
as a storage back-end. You'll need to configure this (e.g. `--storage redis`)
as the default uses the filesystem approach mentioned above. The same `self.db`
will then be passed as a Redis connection object. You will also need to install
additional dependencies using `pip install xbotlib[redis]`.

### Loading Plugins

You can specify a `plugins = [...]` on your bot definition and they will be
automatically loaded when you start your bot.

```python
class MyBot(Bot):
    plugins = ["xep_0066"]
```

See [here](https://slixmpp.readthedocs.io/xeps.html) for the list of supported plugins.

### Serving HTTP

Firstly, you'll need to install additional dependencies.

```bash
$ pip install xbotlib[web]
```

Your bot will run a web server if you configure it to do so. Use the `--serve`
option on the command-line, the `serve = True` configuration option or the
`XBOT_SERVE=True` environment variable.

If you're running your bot locally, just visit
[0.0.0.0:8080](http://0.0.0.0:8080) to see. The default response is just some
placeholder text. You can write your own responses using the
[Bot.serve](#bot-serve-request) function.

`xbotlib` provides a small wrapper API for
[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) which allows you to
easily template and generate HTML. The web server is provided by
[aiohttp](https://docs.aiohttp.org/).

The default template search path is `index.html.j2` in the current working
directory. This can be configured through the usual configuration entrypoints.

Here's a small example that renders a random ASCII letter and uses a stylesheet.

> index.html.j2

```jinja
<html>
<head>
  <style> h1 { color: red; } </style>
</head>
<body>
  <h1>{{ letter }}</h1>
</body>
</html>
```

> bot.py

```python
from string import ascii_letters

async def serve(self, request):
    letter = choice(ascii_letters)
    rendered = self.template.render(letter=letter)
    return self.respond(rendered)
```

Please note the use of the `return` keyword here. The `serve` function must
return a response that will be passed to the web server. Also, the `async`
keyword. This function can handle asynchronous operations and must be marked as
such. You can return any content type that you might find on the web (e.g.
HTML, XML, JSON, audio and maybe even video) but you must specify the
`content_type=...` keyword argument for `respond`.

See the [list of available content
types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types#types)
for more.

If you want to pass data from your `direct`/`group` functions to the `serve`
function, you'll need to make use of [some type of persistent
storage](#storage-back-end). Your `serve` function can read from the storage
back-end and then respond. This is usually as simple as accessing the `self.db`
attribute.

### API Reference

When writing your own bot, you always sub-class the `Bot` class provided from
`xbotlib`. Then if you want to respond to a direct message, you write a
[direct](#botdirectmessage) function. If you want to respond to a group chat
message, you write a [group](#botgroupmessage) function. That's it for the
basics.

#### Bot.direct(message)

Respond to direct messages.

Arguments:

- **message**: received message (see [SimpleMessage](#simplemessage) below for available attributes)

#### Bot.group(message)

Respond to a message in a group chat.

Arguments:

- **message**: received message (see [SimpleMessage](#simplemessage) below for available attributes)

#### Bot.serve(request)

Serve requests via the built-in web server.

See [this section](#serving-http) for more.

Arguments:

- **request**: the web request

### Bot.routes()

Register additional routes for web serving.

See [this section](#serving-http) for more.

This is an advanced feature. Use `self.web.add_routes`.

```python
from aiohttp.web import get

def routes(self):
    self.web.add_routes([get("/foo", self.foo)])
```

#### Bot.setup()

Run some setup logic before starting your bot.

#### SimpleMessage

A simple message interface.

Attributes:

- **text**: the entire text of the message
- **content**: the text of the message after the nick
- **sender**: the user the message came from
- **room**: the room the message came from
- **receiver**: the receiver of the message
- **nick**: the nickname of the sender
- **type**: the type of message
- **url**: The URL of a sent file

#### Bot

> Bot.reply(message, to=None, room=None)

Send a reply back.

Arguments:

- **message**: the message that is sent
- **to**: the user to send the reply to
- **room**: the room to send the reply to

> Bot.respond(response, content_type="text/html")

Return a response via the web server.

Arguments:

- **response**: the text of the response
- **content_type**: the type of response

Other useful attributes on the `Bot` class are:

- **self.db**: The [Redis database](#redis-key-value-storage) if you're using it

## Chatroom

We're lurking in
[xbotlibtest@muc.vvvvvvaria.org](xmpp:xbotlibtest@muc.vvvvvvaria.org?join) if
you want to chat or just invite your bots for testing.

## More Examples

See more examples on [git.vvvvvvaria.org](https://git.vvvvvvaria.org/explore/repos?q=xbotlib&topic=1).

## Deploy your bots

See [bots.varia.zone](https://bots.varia.zone/).

## Roadmap

See the [issue tracker](https://git.autonomic.zone/decentral1se/xbotlib/issues).

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
