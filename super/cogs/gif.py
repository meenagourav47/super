import os
from discord.ext import commands
from super import utils
import aiohttp

class Gif:
    def __init__(self, bot):
        self.bot = bot

    async def _get_url(self, text):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.gifme.io/v1/search',
                data={'key': 'rX7kbMzkGu7WJwvG', 'query': text},
                timeout=5,
            ) as resp:
                data = await resp.json()
                if len(data['data']):
                    return data['data'][0]['link']

            async with session.post(
                'https://rightgif.com/search/web',
                data={'text': text},
                timeout=5,
            ) as resp:
                data = await resp.json()
                return data['url']

    @commands.command(no_pm=True, pass_context=True)
    async def gif(self, ctx):
        utils.send_typing(self, ctx.message.channel)
        text = ctx.message.content.split(' ', 1)[1]
        url = await self._get_url(text)
        await self.bot.say(f'**{text}**: {url}')


def setup(bot):
    bot.add_cog(Gif(bot))
