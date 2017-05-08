import aioredis
from . import settings

conn = None


async def connect():
    global conn
    conn = await aioredis.create_connection(
        (settings.SUPER_REDIS_HOST, settings.SUPER_REDIS_PORT),
    )


async def write(slug, value):
    slug = slug_to_str(slug)
    return await conn.execute('set', slug, value)

async def read(slug):
    slug = slug_to_str(slug)
    return await conn.execute('get', slug, encoding='utf-8')


def get_slug(ctx, command=None, id=None):
    slug = [
        ctx.message.author.server.id,
        id or ctx.message.author.id,
    ]
    if command:
        slug.append(command)
    return slug_to_str(slug)


def slug_to_str(slug):
    if type(slug) == list:
        slug = ':'.join(slug)
    return 'super:' + slug
