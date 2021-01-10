from xbotlib import Bot


class WhisperBot(Bot):
    """Pseudo-anonymous whispering in group chats.

    In order to activate this bot you can invite it to your group chat. Once
    invited, you can directly message the bot outside of the group chat and
    tell it you want it to whisper your message into the group chat. The bot
    will then do this on your behalf and not reveal your identity. This is nice
    when you want to communicate with the group somewhat anonymously.

    The bot accepts messages in the following form.

    whisper:<room>:<message>

    So, I might write it like so.

    whisper:myroom@muc.foo.com:hey, i actually really like avril lavigne!

    """

    def react(self, message):
        """Receive direct messages and pass them to group chats."""
        if message.type == "groupchat":
            return

        if "whisper" in message.body:
            _, room, whisper = message.body.split(":")
            body = f"*whispers* {whisper}"
            self.reply(to=room, body=body, type="groupchat")


WhisperBot()
