import aiohttp
import json
from discord.ext import commands
from super import settings
from super import redis

class np:
    def __init__(self, bot):
        self.bot = bot

    async def lastfm(self, username):
        url = (
            'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks'
            f'&limit=1&user={username}&api_key={settings.SUPER_LASTFM_API_KEY}&format=json'
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = json.loads(await response.read())
        song = {}
        try:
            song['artist'] = response['recenttracks']['track'][0]['artist']['#text']
            album = response['recenttracks']['track'][0]['album']['#text']
            song['album'] = album if len(album) > 0 else None
            song['name'] = response['recenttracks']['track'][0]['name']
        except KeyError:
            pass

        text = f"{song['artist']} - {song['name']}"
        if song['album']:
            text += f" from {song['album']}"
        return text


    @commands.command(no_pm=True, pass_context=True)
    async def np(self, ctx):
        words = ctx.message.content.split(' ')
        slug = redis.get_slug(ctx, 'np')
        try:
            username = words[1]
            await redis.write(slug, username)
        except IndexError:
            username = await redis.read(slug)

        if username is None:
            await self.bot.say(f'Set an username first, e.g.: **{settings.SUPER_PREFIX}np joe**')
            return

        song = await self.lastfm(username)
        await self.bot.say(f'**{username}** now playing: {song}')


def setup(bot):
    bot.add_cog(np(bot))
