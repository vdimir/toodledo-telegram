from tinydb import TinyDB, where
from operator import itemgetter
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


db = TinyDB('db.json')


class UserDbEntry:
    def __init__(self, user_id):
        self.db = db.table('auth_data')
        self.user_id = user_id
        logger.info('Init user %d' % self.user_id)

    def get_token(self):
        r = self.db.get(where('user_id') == self.user_id)
        if r is not None:
            return r['token']

    def upd_token(self, token):
        r = self.db.update({'token': token}, where('user_id') == self.user_id)
        if len(r) == 0:
            self.create(token)
            return
        logger.info('Update user %d' % self.user_id)

    def create(self, token):
        self.db.insert({'user_id': self.user_id, 'token': token})
        logger.info('Create user %d' % self.user_id)


class NotifiedUsers:
    def __init__(self):
        self.db = db.table('notified')

    def get_notified(self):
        res = self.db.all()
        return map(itemgetter('user_id'), res)

    def add_user(self, uid):
        self.db.insert({'user_id': uid})

    def remove_user(self, uid):
        self.db.remove(where('user_id') == uid)
