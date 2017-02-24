from usermanager import ToodledoUser
from toodledo import init_toodledo_client_app
from toodledo.datatypes import Task

from functools import lru_cache
import os
import datetime
init_toodledo_client_app(os.environ['TOODLEDO_CLIENT_ID'],
                         os.environ['TOODLEDO_CLIENT_SECRET'])


class ToodledoClient:
    def __init__(self, uid):
        self.user = ToodledoUser(uid)

    @property
    def auth_url(self):
        return self.user.session.auth_url

    def auth(self, url) -> bool:
        return self.user.session.authorize(url)

    def get_tasks(self, only_id=None, tag=None) -> [Task]:
        params = {'fields': 'duedate,star,tag', 'comp': 0}
        if only_id is not None:
            params['id'] = only_id
        tasks = self.user.tasks.get(params)
        if tag is not None:
            tasks = list(filter(lambda t: tag in t.tags, tasks))
        return tasks

    def make_complete(self, tid):
        task = Task(id_=tid, completed_date=datetime.date.today())
        res = self.user.tasks.edit(task)
        if len(res) != 1:
            return False
        return str(res[0].get('id')) == str(tid)

    def add_task(self, task):
        res = self.user.tasks.add(task)
        return res


@lru_cache(maxsize=500)
def with_user(user_id) -> ToodledoClient:
    return ToodledoClient(user_id)
