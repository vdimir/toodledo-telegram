from usermanager import ToodledoUser
from toodledo import NotAuthorizingError, init_toodledo_client_app

from functools import lru_cache
import os

init_toodledo_client_app(os.environ['TOODLEDO_CLIENT_ID'],
                         os.environ['TOODLEDO_CLIENT_SECRET'])


def task_str(task):
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

    def auth(self, url) -> str:
        r = self.user.session.authorize(url)
        if r:
            return "Authorizing success!"
        else:
            return "Wrong auth data!"

    @not_authorized_handle
    def get_tasks(self) -> str:
        tasks = self.user.tasks.get({'fields': 'duedate'})
        return str.join("\n", map(task_str, tasks))


@lru_cache(maxsize=500)
def with_user(user_id) -> ToodledoClient:
    return ToodledoClient(user_id)
