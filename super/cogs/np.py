import asyncio
import aiohttp
import json
from discord.ext import commands
from super import settings, redis, utils
from datetime import datetime
import time
import humanize

class np:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def __exit__(self):
        self.session.close()
    

    def _lastfm_track_to_song(self, track):
        song = {
            'time': 0,
            'playing_now': False,
        }
        try:
            song['artist'] = track['artist']['#text']
            album = track['album']['#text']
            song['album'] = album if len(album) > 0 else None
            song['name'] = track['name']

            if 'date' in track:
                song['time'] = int(track['date']['uts'])
            elif '@attr' in track and 'nowplaying' in track['@attr']:
                song['time'] = int(time.time())
                song['playing_now'] = True
        except KeyError:
            pass

        return song


    def _lastfm_song_to_str(self, lfm, nick, song):
        return ' '.join([
            f'**{lfm}**',
            f'({nick})' if nick else '',
            f"now playing: **{song['artist']} - {song['name']}**",
            f"from **{song['album']}**" if song['album'] else '',
        ])


    async def lastfm(self, lfm, nick=None):
        url = (
            'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks'
            f'&limit=1&user={lfm}&api_key={settings.SUPER_LASTFM_API_KEY}&format=json'
        )
        async with self.session.get(url) as response:
            response = json.loads(await response.read())
        track = response['recenttracks']['track'][0]
        song = self._lastfm_track_to_song(track)
        return {
            'song': song,
            'formatted': self._lastfm_song_to_str(lfm, nick, song),
        }


    @commands.command(no_pm=True, pass_context=True)
    async def np(self, ctx):
        """Get now playing song from last.fm"""
        utils.send_typing(self, ctx.message.channel)
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
        lastfm_data = await self.lastfm(username)
        await self.bot.say(lastfm_data['formatted'])


    @commands.command(no_pm=True, pass_context=True, name='wp')
    async def wp(self, ctx):
        """Get now playing song from last.fm, for the whole server"""
        utils.send_typing(self, ctx.message.channel)
        message = ['Users playing music in this server:']
        tasks = []
        for member in ctx.message.server.members:
            id, name = member.id, member.display_name
            lfm = await redis.read(redis.get_slug(ctx, 'np', id=id))
            if not lfm:
                continue
            tasks.append(self.lastfm(lfm, name))

        for lastfm_data in await asyncio.gather(*tasks):
            if lastfm_data['song']['playing_now']:
                message.append(lastfm_data['formatted'])
        if len(message) == 1:
            message.append('Nobody. :disappointed:')
        await self.bot.say('\n'.join(message))


def setup(bot):
    bot.add_cog(np(bot))
