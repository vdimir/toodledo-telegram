from .usermanager import ToodledoUser
from .datatypes import Task
from toodledocore.schemas import TaskSchema
import datetime

tasks_schema = TaskSchema(many=True)
tasks_schema.__model__ = Task

fields = 'duedate,star,tag'


def dumps_tasks(tasks):
    if not isinstance(tasks, list):
        tasks = [tasks]
    return tasks_schema.dumps(tasks).data,


def send_tasks_params(tasks):
        params = {
            "tasks": dumps_tasks(tasks),
            "fields": fields
        }
        return params


class ToodledoClient:
    def __init__(self, uid):
        self.user = ToodledoUser(uid)

    @property
    def auth_url(self):
        return self.user.session.auth_url

    def auth(self, url) -> bool:
        return self.user.session.authorize(url)

    def get_tasks(self, only_id=None, tag=None) -> [Task]:
        params = {'fields': fields, 'comp': 0}
        if only_id is not None:
            params['id'] = only_id
        data = self.user.tasks.get(params)
        tasks = tasks_schema.load(data[1:]).data
        if tag is not None:
            tasks = list(filter(lambda t: tag in t.tags, tasks))
        return tasks

    def make_complete(self, tid):
        task = {'id_': tid, 'completed_date': datetime.date.today()}
        res = self.user.tasks.edit(send_tasks_params(task))
        if len(res) != 1:
            return False
        return res[0].get('id') == int(tid)

    def delete_task(self, tid):
        params = {'tasks': [tid]}
        res = self.user.tasks.edit(params)
        if len(res) != 1:
            return False
        return res[0].get('id') == int(tid)

    def add_task(self, task):
        res = self.user.tasks.add(send_tasks_params(task))
        return res
