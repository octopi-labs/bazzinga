
import redis
from shorten import (NamespacedFormatter, UUIDTokenGenerator, alphabets,
                     make_store)

from libapp.config import shortconf


def init_app(app):
    redis_client = redis.Redis(host=shortconf.SHORTNER_HOST,
                               port=shortconf.SHORTNER_PORT, db=shortconf.SHORTNER_DB)
    formatter = NamespacedFormatter(shortconf.FORMATTER)
    token_gen = UUIDTokenGenerator()

    store_params = {
        shortconf.SHORTNER_CLIENT: redis_client,
        "counter_key": shortconf.COUNTER_KEY,
        "formatter": formatter,
        "token_gen": token_gen,
        "alphabet": alphabets.URLSAFE_DISSIMILAR
    }
    stored = make_store(name=shortconf.SHORTNER_STORE,
                        min_length=shortconf.MIN_LENGTH, **store_params)
    return stored
