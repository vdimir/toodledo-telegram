from database import UserDbEntry
from toodledocore import ToodledoSession, ToodledoApi


class ToodledoUser:
    def __init__(self, user_id):
        user = UserDbEntry(user_id)
        self.session = ToodledoSession(user.get_token(),
                                       user.upd_token)
        self.tasks = ToodledoApi(self.session, 'tasks')
        self.account = ToodledoApi(self.session, 'account')

    def authorize(self, redirect_url):
        self.session.authorize(redirect_url)
