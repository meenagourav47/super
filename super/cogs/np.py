import aiohttp
import json
from discord.ext import commands
from super import settings
from super import redis
from datetime import datetime
import time
import humanize

class np:
    def __init__(self, bot):
        self.bot = bot

    async def lastfm(self, lfm, nick=None, timeago=False):
        url = (
            'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks'
            f'&limit=1&user={lfm}&api_key={settings.SUPER_LASTFM_API_KEY}&format=json'
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = json.loads(await response.read())
        song = {
            'time': 0,
        }
        track = response['recenttracks']['track'][0]
        try:
            song['artist'] = track['artist']['#text']
            album = track['album']['#text']
            song['album'] = album if len(album) > 0 else None
            song['name'] = track['name']

            if 'date' in track:
                song['time'] = int(track['date']['uts'])
            elif '@attr' in track and 'nowplaying' in track['@attr']:
                song['time'] = int(time.time())
            song['timeago'] = humanize.naturaltime(datetime.fromtimestamp(song['time']))
        except KeyError:
            pass

        return ' '.join([
            f'**{lfm}**',
            f'({nick})' if nick else '',
            f"now playing: **{song['artist']} - {song['name']}**",
            f"from **{song['album']}**" if song['album'] else '',
            f"{song['timeago']}" if timeago else '',
        ])

    @commands.command(no_pm=True, pass_context=True)
    async def np(self, ctx):
        """Get now playing song from last.fm"""
        await self.bot.send_typing(ctx.message.channel)
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

        await self.bot.say(await self.lastfm(username))

    @commands.command(no_pm=True, pass_context=True, name='wp')
    async def wp(self, ctx):
        """Get now playing song from last.fm, for the whole server"""
        await self.bot.send_typing(ctx.message.channel)
        message = ['Users playing music in this server:']
        for member in ctx.message.server.members:
            id, name = member.id, member.display_name

            lfm = await redis.read(redis.get_slug(ctx, 'np', id=id))
            if lfm:
                message.append(await self.lastfm(lfm, name, timeago=True))

        await self.bot.say('\n'.join(message))


def setup(bot):
    bot.add_cog(np(bot))
