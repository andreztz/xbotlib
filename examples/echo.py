from xbotlib import Bot


class EchoBot(Bot):
    """Gives back what you sent it.

    Just direct message the bot and see if you get back what you sent.

    """

    def reply_direct_chat(self, message):
        """Send back what we get."""
        self.send_direct_chat(to=message.sender, body=message.body)


EchoBot()
