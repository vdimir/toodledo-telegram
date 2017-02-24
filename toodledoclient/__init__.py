from .toodledo_client import ToodledoClient

from functools import lru_cache
import os

from toodledocore import init_toodledo_client_app
init_toodledo_client_app(os.environ['TOODLEDO_CLIENT_ID'],
                         os.environ['TOODLEDO_CLIENT_SECRET'])


@lru_cache(maxsize=500)
def with_user(user_id) -> ToodledoClient:
    return ToodledoClient(user_id)
