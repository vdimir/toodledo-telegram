from tinydb import TinyDB, where

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


db = TinyDB('db.json')


class UserDbEntry:
    def __init__(self, user_id):
        self.user_id = user_id
        logger.info('Init user %d' % self.user_id)

    def get_token(self):
        return db.get(where('user_id') == self.user_id)['token']

    def upd_token(self, token):
        r = db.update({'token': token}, where('user_id') == self.user_id)
        if len(r) == 0:
            self.create(token)
            return
        logger.info('Update user %d' % self.user_id)

    def create(self, token):
        db.insert({'user_id': self.user_id, 'token': token})
        logger.info('Create user %d' % self.user_id)
