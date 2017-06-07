import asyncio

def send_typing(self, channel):
        return asyncio.ensure_future(
            self.bot.send_typing(channel),
            loop=asyncio.get_event_loop(),
        )
