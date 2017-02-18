from database import UserDbEntry
from toodledo import ToodledoSession, ToodledoRequest
from functools import lru_cache


class ToodledoUser:
    def __init__(self, user_id):
        self.user_db = UserDbEntry(user_id)
        self.session = ToodledoSession(self.user_db.get_token(),
                                       self.user_db.upd_token)
        self.tasks = ToodledoRequest(self.session, 'tasks')

    def authorize(self, redirect_url):
        self.session.authorize(redirect_url)


@lru_cache(maxsize=500)
def user(user_id) -> ToodledoUser:
    return ToodledoUser(user_id)
