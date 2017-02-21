from usermanager import ToodledoUser
from toodledo import NotAuthorizingError, init_toodledo_client_app
from toodledo.datatypes import Task

from functools import lru_cache
import os
import datetime
init_toodledo_client_app(os.environ['TOODLEDO_CLIENT_ID'],
                         os.environ['TOODLEDO_CLIENT_SECRET'])


def task_str(task: Task):
    x = '[x]' if task.completed else '[ ]'
    due = '' if task.duedate is None else task.duedate.strftime("<i>%d %b, %A</i>")
    return str.format("{x} {title} {due}", x=x, title=task.title, due=due)


def not_authorized_handle(func):
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except NotAuthorizingError:
            return "Not authorized\n" + self.user.session.auth_url
    return wrap


class ToodledoClient:
    def __init__(self, uid):
        self.user = ToodledoUser(uid)

    def auth(self, url) -> bool:
        return self.user.session.authorize(url)

    @not_authorized_handle
    def get_tasks(self, only_id=None) -> [Task]:
        params = {'fields': 'duedate', 'comp': 0}
        if only_id is not None:
            params['id'] = only_id
        tasks = self.user.tasks.get(params)
        return tasks

    def make_complete(self, tid):
        task = Task(id_=tid, completed_date=datetime.date.today())
        res = self.user.tasks.edit(task)
        if len(res) != 1:
            return False
        return str(res[0].get('id')) == str(tid)


@lru_cache(maxsize=500)
def with_user(user_id) -> ToodledoClient:
    return ToodledoClient(user_id)
