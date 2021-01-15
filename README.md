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
doing things.

## Install

```sh
$ pip install xbotlib
```

## Example

Put the following in a `echo.py` file.

`xbotlib` provides a number of example bots which you can use to get moving
fast and try things out.

```python
from xbotlib import EchoBot

EchotBot()
```

And then `python echo.py`. You will be asked a few questions in order to load
the account details that your bot will be using. This will generate a
`bot.conf` file in the same working directory for further use. See the
[configuration](#configure-your-bot) section for more.

Here's the code for the `EchoBot`.

```python
class EchoBot(Bot):
    def direct(self, message):
        self.reply(message.body, to=message.sender)

    def group(self, message):
        if "echobot" in message.body:
            self.reply(message.body.split(":")[-1], room=message.room)
```

Read more in the [API reference](#api-reference) for how to write your own bots.

## All examples

- **EchoBot**: Sends back what you sent it
- **WhisperBot**: Anonymous whispering in group chats

See [xbotlib.py](./xbotlib.py) for all example bots.

## API Reference

When writing your own bot, you always sub-class the `Bot` class provided from
`xbotlib`. Then if you want to respond to a direct message, you write a
[direct](#botdirectmessage) function. If you want to respond to a group chat
message, you write a [group](#botgroupmessage) function.

### Bot.direct(message)

Respond to direct messages.

Arguments:

- **message**: received message (see [SimpleMessage](#simplemessage) below for available attributes)

### Bot.group(message)

Respond to a message in a group chat.

Arguments:

- **message**: received message (see [SimpleMessage](#simplemessage) below for available attributes)

### SimpleMessage

A simple message interface.

Attributes:

- **body**: the body of the message
- **sender**: the user the message came from
- **room**: the room the message came from
- **receiver**: the receiver of the message
- **nickname**: the nickname of the sender
- **type**: the type of message (`chat` or `groupchat`)

## Documenting your bot

Add a `help = "my help"` to your `Bot` class like so.

```python
class MyBot(Bot):
    help = "My help"
```

The bot will then respond to:

- `!uptime` commands in direct messages
- `<nick>:!uptime` commands in group chats (use your own nick)

## Avatars

By default, `xbotlib` will look for an `avatar.png` file alongside your Python
script which contains your bot implementation. You can also specify another
path using the `--avatar` option on the command-line interface. The images
should ideally have a height of `64` and a width of `64` pixels each.

## Configure your bot

All the ways you can pass configuration details to your bot.

### Using the bot.conf

If you run simply run your Python script which contains the bot then `xbotlib`
will generate a configuration for you by asking a few questions. This is the
simplest way to run your bot locally.

### Using the command-line interface

Every bot accepts a number of comand-line arguments to load configuration. You
can use the `--help` option to see what is available (e.g. `python bot.py --help`).

### Using the environment

`xbotlib` will try to read the following configuration values from the
environment if it cannot read them from a configuration file or the
command-line interface. This can be useful when doing remote server
deployments.

- **XBOT_ACCOUNT**: The bot account
- **XBOT_PASSWORD**: The bot password
- **XBOT_NICK**: The bot nickname

## Roadmap

See the [issue tracker](https://git.autonomic.zone/decentral1se/xbotlib/issues).

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
