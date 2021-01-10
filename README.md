# xbotlib

## XMPP bots for humans

> status: experimental

A friendly lightweight wrapper around
[slixmpp](https://slixmpp.readthedocs.io/) for writing XMPP bots in Python. The
goal is to make writing and running XMPP bots easy and fun.

`xbotlib` is a [single file implementation](./xbotlib.py) which can easily be
understood and extended. It provides a small API surface which reflects the
`slixmpp` way of doing things.

## Install

```sh
$ pip install xbotlib
```

## Example

```python
from xbotlib import Bot

class EchoBot(Bot):
    def react(self, message):
        if message.type == "chat":
          self.reply(to=message.sender, body=message.body)

MyBot()
```

And then `python echo.py`. You will be asked a few questions like which account
details your bot will be using. This will generate a `bot.conf` file in the
same working directory for further use.

## More Examples

- **[EchoBot](./examples/echo.py)**: Sends back what you sent it
- **[WhisperBot](./examples/whisper.py)**: Pseudo-anonymous whispering in group chats

See the [examples](./examples/) directoy for all listings.

## API Reference

Your bot always sub-classes the `Bot` class provided from `xbotlib`. All
underling functions can be extended. For example, if you want to enable more
plugins or add different functionality. If something feels awkwardthen please
raise a ticket for that. Seamlessness is still a bitch but we're trying anyway.

### Bot.react

A function which you define in your bot implementation in order to respond to
chat messages. You can respond to both direct messages and group chat messages
in this function by checking the `message.type` which can be either `chat` or
`groupchat`.

Arguments:

- **message**: sent message and metadata (see [message](#message) reference below)

### Bot.reply

Send back a response to a direct chat message.

Arguments:

- **to**: which user account to reply to (direct chat)
- **room**: which room to reply to (group chat)
- **body**: the message to send

### Message

A simple message format.

Attributes:

- **body**: the body of the message
- **sender**: the sender of the message
- **receive**: the receive of the message
- **nickname**: the nickname of the sender
- **type**: the type of message (`chat` or `groupchat`)

## Roadmap

- The library only handles reactions. The bots can only send messages when they
  receive a message. It would be nice to allow for sending messages at specific
  times.

- Extend the `bot.conf` to allow for multiple bot configurations.

- Sort out something for how to deploy them. It's easy to run them locally but
  hard to run them on a server. Maybe something can be done for that as well.

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
