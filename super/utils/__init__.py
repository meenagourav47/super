from .. import settings

from .chat import send_typing
from .redis import SuperRedis

R = SuperRedis(
    host=settings.SUPER_REDIS_HOST,
    port=settings.SUPER_REDIS_PORT,
)
