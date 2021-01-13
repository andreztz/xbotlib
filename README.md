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
    """Gives back what you sent it.

    In group chats, it responds to the following format.

    echobot:foo
    """
    def react(self, message):
        if message.type == "chat":
            # Reply to direct messages
            self.reply(message.body, to=message.source)

        if message.type == "groupchat" and "echobot" in message.body:
            # Parse and reply group chat messages
            _, to_echo = message.body.split(":")
            self.reply(to_echo, room=message.room)
```

## All examples

- **EchoBot**: Sends back what you sent it
- **WhisperBot**: Pseudo-anonymous whispering in group chats

See [xbotlib.py](./xbotlib.py) for all example bots.

## API Reference

When writing your own bot, you always sub-classes the `Bot` class provided from
`xbotlib`. All underling functions can be extended. For example, if you want to
enable more plugins or add different functionality. If something feels awkward
then please raise a ticket for that. Seamlessness is still a bitch but we're
trying anyway.

> Bot.react(message)

A function which you define in your bot implementation in order to respond to
chat messages. You can respond to both direct messages and group chat messages
in this function by checking the `message.type` which can be either `chat` or
`groupchat`.

Arguments:

- **message**: sent message and metadata (see [message](#message) reference below)

> Bot.reply(body, to=None, room=None)

Send back a response to a direct chat message.

Arguments:

- **body**: the message to send
- **to**: which user account to reply to (direct chat)
- **room**: which room to reply to (group chat)

> SimpleMessage

A simple message format. This is the type that you work with when your function
accepts a `message` argument.

Attributes:

- **body**: the body of the message
- **source**: where the message came from (can be a user or a room)
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
