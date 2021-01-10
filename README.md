# xbotlib

## XMPP bots for humans

## Install

```sh
$ pip install xbotlib
```

## Example

```python
from xbotlib import Bot

class EchoBot(Bot):
    def react(self, msg):
        self.reply(to=message.sender, body=message.body)

MyBot()
```

And then `python echo.py`.

## More Examples

- **[EchoBot](./examples/echo.py)**: Sends back what you sent it
- **[WhisperBot](./examples/whisper.py)**: Pseudo-anonymous whispering in group chats

See the [examples](./examples/) directoy for all listings.
