import discord
import asyncio
import aiohttp
import os
import json

SUPER_DISCORD_TOKEN = os.environ['SUPER_DISCORD_TOKEN']
SUPER_LASTFM_API_KEY = os.environ['SUPER_LASTFM_API_KEY']

client = discord.Client()

@client.event
async def on_ready():
    print('Super ready!')

@client.event
async def on_message(message):
    if message.content.startswith('.np'):
        words = message.content.split(' ')
        try:
            username = words[1]
        except IndexError:
            username = 'chauffer9001'
        song = await get_playing_song(username)
        await client.send_message(message.channel, f'**{username}** now playing: {song}')

async def get_playing_song(username):
    url = (
        'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks'
        f'&limit=1&user={username}&api_key={SUPER_LASTFM_API_KEY}&format=json'
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response = json.loads(await response.read())
    song = []
    try:
        song.append(response['recenttracks']['track'][0]['artist']['#text'])

        album = response['recenttracks']['track'][0]['album']['#text']
        if len(album) > 0:
            song.append(album)
        song.append(response['recenttracks']['track'][0]['name'])
    except KeyError:
        pass

    return ' - '.join(song)



client.run(SUPER_DISCORD_TOKEN, bot=True)