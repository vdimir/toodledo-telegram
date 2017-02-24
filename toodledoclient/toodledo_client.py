from .usermanager import ToodledoUser
from .datatypes import Task

from toodledocore.schemas import TaskSchema

import datetime

tasks_schema = TaskSchema(many=True)
tasks_schema.__model__ = Task

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
        data = self.user.tasks.get(params)
        tasks = tasks_schema.load(data[1:]).data
        if tag is not None:
            tasks = list(filter(lambda t: tag in t.tags, tasks))
        return tasks

    def make_complete(self, tid):
        task = Task(id_=tid, completed_date=datetime.date.today())
        params = {
            "tasks": tasks_schema.dumps([task]).data,
            "fields": 'duedate,star,tag'
        }
        res = self.user.tasks.edit(params)
        if len(res) != 1:
            return False
        return str(res[0].get('id')) == str(tid)

    def add_task(self, task):
        params = {
            "tasks": tasks_schema.dumps([task]).data,
            "fields": 'duedate,star,tag'
        }
        res = self.user.tasks.add(params)
        return res
