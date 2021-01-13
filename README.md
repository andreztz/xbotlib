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

Put the following in a `echo.py` file. `xbotlib` provides a number of example
bots which you can use to get moving fast and try things out.

```python
from xbotlib import EchoBot

EchotBot()
```

And then `python echo.py`. You will be asked a few questions like which account
details your bot will be using.

This will generate a `bot.conf` file in the same working directory for further use.

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
- **WhisperBot**: Pseudo-anonymous whispering in group chats

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

## Configure your bot

### Using the environment

You can pass the `--no-input` option to your script invocation (e.g. `python bot.py --no-input`).

`xbotlib` will try to read the following configuration values from the environment.

- **XBOT_JID**: The username of the bot account
- **XBOT_PASSWORD**: The password of the bot account
- **XBOT_ROOM**: The room that the bot can join
- **XBOT_NICK**: The nickname that the bot uses

## Roadmap

See the [issue tracker](https://git.autonomic.zone/decentral1se/xbotlib/issues).

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
