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

```python
from xbotlib import Bot

class EchoBot(Bot):
    def react(self, message):
        if message.type == "chat":
          self.reply(message.body, to=message.sender)

MyBot()
```

And then `python echo.py`. You will be asked a few questions like which account
details your bot will be using.

This will generate a `bot.conf` file in the same working directory for further use.

## More Examples

- **[EchoBot](./examples/echo.py)**: Sends back what you sent it
- **[WhisperBot](./examples/whisper.py)**: Pseudo-anonymous whispering in group chats

See the [examples](./examples/) directoy for all listings.

## API Reference

Your bot always sub-classes the `Bot` class provided from `xbotlib`. All
underling functions can be extended. For example, if you want to enable more
plugins or add different functionality. If something feels awkward then please
raise a ticket for that. Seamlessness is still a bitch but we're trying anyway.

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

> EasyMessage

A simple message format. This is the type that you work with when your function
accepts a `message` argument.

Attributes:

- **body**: the body of the message
- **sender**: the sender of the message
- **receive**: the receive of the message
- **nickname**: the nickname of the sender
- **type**: the type of message (`chat` or `groupchat`)

## Configure your bot

### Using the environment

You can pass the `--no-input` option to your script invocation (e.g. `python bot.py --no-input`).

`xbotlib` will try to read the following configuration values from the environment.

- **XBOT_JID**
- **XBOT_PASSWORD**
- **XBOT_ROOM**
- **XBOT_NICK**

## Roadmap

See the [issue tracker](https://git.autonomic.zone/decentral1se/xbotlib/issues).

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
