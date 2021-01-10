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
        self.reply(f"echo: {msg}")

MyBot()
```

And then `python echo.py`.

## API

TODO.
