from xbotlib import Bot


class EchoBot(Bot):
    """Gives back what you sent it.

    Just direct message the bot and see if you get back what you sent.

    """

    def react(self, message):
        """Send back what we get."""
        self.reply(to=message.sender, body=message.body)


EchoBot()
