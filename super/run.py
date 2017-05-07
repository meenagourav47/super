from discord.ext import commands
import discord
import aiohttp
import json

from . import settings
from . import redis

description = "Super is Yet Another Yet Another Discord Bot. github.com/chauffer/super"


bot = commands.Bot(
    command_prefix=settings.SUPER_PREFIX,
    description=description,
    pm_help=None,
)

extensions = [
    'super.cogs.np',
    'super.cogs.markov',
]

@bot.event
async def on_ready():
    await redis.connect()
    print('Super ready!')

def main():
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
    
    bot.run(settings.SUPER_DISCORD_TOKEN, bot=True)

if __name__ == '__main__':
    main()
