from xbotlib import Bot


class EchoBot(Bot):
    """SYN/ACK bot for testing things work.

    Just direct message the bot and see if you get back what you sent. If so,
    then you know your setup is working.

    """

    def react(self, message):
        """Send back what we get."""
        self.reply(to=message.sender, body=message.body)


EchoBot()
