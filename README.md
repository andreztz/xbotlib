# xbotlib

[![PyPI version](https://badge.fury.io/py/xbotlib.svg)](https://badge.fury.io/py/xbotlib)
[![Build Status](https://drone.autonomic.zone/api/badges/decentral1se/xbotlib/status.svg?ref=refs/heads/main)](https://drone.autonomic.zone/decentral1se/xbotlib)

## XMPP bots for humans

> status: experimental

A friendly lightweight wrapper around
[slixmpp](https://slixmpp.readthedocs.io/) for writing XMPP bots in Python. The
goal is to make writing and running XMPP bots easy and fun. `xbotlib` is a
[single file implementation](./xbotlib.py) which can easily be understood and
extended. It provides a small API surface which reflects the `slixmpp` way of
doing things. The `xbotlib` source code and ideas are largely
borrowed/stolen/adapted/reimagined from the XMPP bot experiments that have gone
on and are still going on in
[Varia](https://git.vvvvvvaria.org/explore/repos?tab=&sort=recentupdate&q=bots).

We're lurking in
[xbotlibtest@muc.vvvvvvaria.org](xmpp:xbotlibtest@muc.vvvvvvaria.org?join) if
you want to chat or just invite your bots for testing.

- [Install](#install)
- [Example](#example)
- [API Reference](#api-reference)
  - [Bot.direct(message)](#bot-direct-message)
  - [Bot.group(message)](#bot-group-message)
  - [Bot.serve(request)](#bot-serve-request)
  - [SimpleMessage](#simplemessage)
  - [Bot](#bot)
- [Working with your bot](#working-with-your-bot)
  - [Documentation](#documentation)
  - [Commands](#commands)
  - [Avatars](#avatars)
  - [Configuration](#configuration)
    - [Using the `.conf` configuration file](#using-the--conf--configuration-file)
    - [Using the command-line interface](#using-the-command-line-interface)
    - [Using the environment](#using-the-environment)
  - [Persistent storage](#persistent-storage)
    - [File system](#file-system)
    - [Redis key/value storage](#redis-key-value-storage)
  - [Loading Plugins](#loading-plugins)
  - [Serving HTTP](#serving-http)
- [Deploy your bots](#deploy-your-bots)
- [Roadmap](#roadmap)
- [Changes](#changes)
- [License](#license)

## Install

```sh
$ pip install xbotlib
```

## Example

Put the following in a `echo.py` file. This bot is pretty simple: it echoes
back whatever message you send it. It is an easy way to get started.

```python
from xbotlib import Bot

class EchoBot(Bot):

    def direct(self, message):
        return self.reply(message.text, to=message.sender)

    def group(self, message):
        return self.reply(message.content, room=message.room)
```

And then `python echo.py`. You will be asked a few questions in order to load
the account details that your bot will be using. This will generate an
`echobot.conf` file in the same working directory for further use. See the
[configuration](#configure-your-bot) section for more.

Read more in the [API reference](#api-reference) for how to write your own bots.

See more examples on [git.vvvvvvaria.org](https://git.vvvvvvaria.org/explore/repos?q=xbotlib&topic=1).

## API Reference

When writing your own bot, you always sub-class the `Bot` class provided from
`xbotlib`. Then if you want to respond to a direct message, you write a
[direct](#botdirectmessage) function. If you want to respond to a group chat
message, you write a [group](#botgroupmessage) function. That's it for the
basics.

### Bot.direct(message)

Respond to direct messages.

Arguments:

- **message**: received message (see [SimpleMessage](#simplemessage) below for available attributes)

### Bot.group(message)

Respond to a message in a group chat.

Arguments:

- **message**: received message (see [SimpleMessage](#simplemessage) below for available attributes)

### Bot.serve(request)

Serve requests via the built-in web server.

Arguments:

- **request**: the web request

### SimpleMessage

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

### Bot

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

## Working with your bot

### Documentation

Add a `help = "my help"` to your `Bot` class like so.

```python
class MyBot(Bot):
    help = "My help"
```

See more in the [commands](#commands) section on how to use this.

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

## Configuration

All the ways you can pass configuration details to your bot. There are three
ways to configure your bot, the configuration file, command-line interface and
the environment. Use whichever one suits you best. The values are loaded in the
following order: command-line > configuration file > environment.

#### Using the `.conf` configuration file

If you run simply run your Python script which contains the bot then `xbotlib`
will generate a configuration for you by asking a few questions. This is the
simplest way to run your bot locally.

Here is an example of a working configuration.

```conf
[echobot]
account = echobot@vvvvvvaria.org
password = ...thepassword...
nick = echobot
rooms = test1@muc.example.com, test2@muc.example.com
```

#### Using the command-line interface

Every bot accepts a number of comand-line arguments to load configuration. You
can use the `--help` option to see what is available (e.g. `python bot.py --help`).

```
usage: bot.py [-h] [-d] [-a ACCOUNT] [-p PASSWORD] [-n NICK]
              [-av AVATAR] [-ru REDIS_URL] [-r ROOMS [ROOMS ...]]
              [--no-auto-join]

XMPP bots for humans

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable verbose debug logs
  -a ACCOUNT, --account ACCOUNT
                        Account for the bot account
  -p PASSWORD, --password PASSWORD
                        Password for the bot account
  -n NICK, --nick NICK  Nickname for the bot account
  -av AVATAR, --avatar AVATAR
                        Avatar for the bot account
  -ru REDIS_URL, --redis-url REDIS_URL
                        Redis storage connection URL
  -r ROOMS [ROOMS ...], --rooms ROOMS [ROOMS ...]
                        Rooms to automatically join
  --no-auto-join        Disable automatically joining rooms when invited
  -pt PORT, --port PORT
                        The port to serve from
  -t TEMPLATE, --template TEMPLATE
                        The template to render
```

#### Using the environment

`xbotlib` will try to read the following configuration values from the
environment if it cannot read them from a configuration file or the
command-line interface. This can be useful when doing remote server
deployments.

- **XBOT_ACCOUNT**: The bot account
- **XBOT_PASSWORD**: The bot password
- **XBOT_NICK**: The bot nickname
- **XBOT_AVATAR**: The bot avatar icon
- **XBOT_REDIS_URL**: Redis key store connection URL
- **XBOT_ROOMS**: The rooms to automatically join
- **XBOT_NO_AUTO_JOIN**: Disable auto-joining on invite
- **XBOT_PORT**: The port to serve from

### Persistent storage

#### File system

Just use your local file system as you would in any other Python script. Please
note that when you deploy your bot, you might not have access to this local
filesystem in the same location. For remote server deployments
[Redis](#redis-key-value-storage) can be more convenient.

#### Redis key/value storage

`xbotlib` supports using [Redis](https://redis.io/) as a storage back-end. It
is simple to work with because the interface is exactly like a dictionary. You
can quickly run Redis locally using [Docker](https://docs.docker.com/engine/install/debian/)
(`docker run --network=host --name redis -d redis`) or if you're on a Debian system you can
also `sudo apt install -y redis`.

You can configure the connection URL using the command-line interface,
configuration or environment. Here is an example using the environment.

```bash
$ export XBOT_REDIS_URL=redis://localhost:6379/0
```

And you access the interface via the `self.db` attribute.

```python
def direct(self, message):
    self.db["mykey"] = message.text
```

You should see `INFO Successfully connected to storage` when your bot
initialises. Please see the
[redis-py](https://redis-py.readthedocs.io/en/stable/) API documentation for
more.

### Loading Plugins

You can specify a `plugins = [...]` on your bot definition and they will be
automatically loaded.

```python
class MyBot(Bot):
    plugins = ["xep_0066"]
```

### Serving HTTP

Your bot will automatically be running a web server at port `8080` when it is
run. If you're running your bot locally, just visit
[0.0.0.0:8080](http://0.0.0.0:8080) to see. The default response is just some
placeholder text. You can write your own responses using the
[Bot.serve](#bot-serve-request) function.

`xbotlib` provides a small wrapper API for
[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/) which allows you to
easily template and generate HTML. The web server is provided by
[aiohttp](https://docs.aiohttp.org/).

The default template search path is `index.html.j2` in the current working
directory. This can be configured through the usual configuration entrypoints.

Here's a small example that renders a random ASCII letter.

```jinja
<h1>{{ letter }}</h1>
```

```python
from string import ascii_letters

def serve(self, request):
    letter = choice(ascii_letters)
    rendered = self.template.render(letter=letter)
    return self.respond(body=rendered)
```

If you want to pass data from your `direct`/`group` functions to the `serve`
function, you'll need to make use of [some type of persistent
storage](#persistent-storage). Your `serve` function can read from the database
or file system and then respond with generated HTML from there.

Having your bot avaible on the web is useful for doing healthchecks with
something like [statping](https://statping.com/) so you be sure that your bot
is up and running.

## Deploy your bots

See [bots.varia.zone](https://bots.varia.zone/).

## Roadmap

See the [issue tracker](https://git.autonomic.zone/decentral1se/xbotlib/issues).

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
