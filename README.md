# xbotlib

## XMPP bots for humans

A friendly lightweight wrapper around [slixmpp](https://slixmpp.readthedocs.io/).

`xbotlib` doesn't want to obscure the workings of the underlying library or
invent a totally new API. To this end, `xbotlib` is a [single file
implementation](./xbotlib.py) which can easily be understood and extended. It
provides a small API surface which reflects the `slixmpp` way of doing things.

The goal is to make writing and running XMPP bots in Python easy and fun.

## Install

```sh
$ pip install xbotlib
```

## Example

```python
from xbotlib import Bot

class EchoBot(Bot):
    def reply_direct_chat(self, message):
        self.send_direct_chat(to=message.sender, body=message.body)

MyBot()
```

And then `python echo.py`.

## More Examples

- **[EchoBot](./examples/echo.py)**: Sends back what you sent it
- **[WhisperBot](./examples/whisper.py)**: Pseudo-anonymous whispering in group chats

See the [examples](./examples/) directoy for all listings.

## API Reference

Your bot always sub-classes the `Bot` class provided from `xbotlib`. All
underling functions can be extended. For example, if you want to enable more
plugins or add different functionality. If something feels awkward then please
raise a ticket for that. See the one file [source](./xbotlib.py) here.

### send_direct_chat

Send back a response to a direct chat message.

Arguments:

- **to**: who to send it to (can be a user or a room)
- **body**: the message to send

### send_group_chat

Send back a response to a group chat message.

Arguments:

- **to**: who to send it to (can be a user or a room)
- **body**: the message to send

## Roadmap

- The library only handles reactions. The bots can only send messages when they
  receive a message. It would be nice to allow for sending messages at specific
  times.

- Extend the `bot.conf` to allow for multiple bot configurations.

- Sort out something for how to deploy them. It's easy to run them locally but
  hard to run them on server. Maybe something can be done for that as well.

## Changes

See the [CHANGELOG.md](./CHANGELOG.md).

## License

See the [LICENSE](./LICENSE.md).
