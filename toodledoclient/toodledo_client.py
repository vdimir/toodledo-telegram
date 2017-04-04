from .usermanager import ToodledoUser
from .datatypes import Task
from toodledocore.schemas import TaskSchema
import datetime
from pysistence import make_dict
from functional import compose

from utils import maybe_list, andf, tuple_func
import time
from utils import attrgetter, Inf

import logging
logger = logging.getLogger(__name__)

task_schema = TaskSchema()
task_schema.__model__ = Task

params = make_dict(fields='duedate,star,tag,priority,note')


class TaskCache:
    def __init__(self, api):
        self.api = api
        self.lastedit = 0
        self.lastdelete = 0
        self.stored_tasks = {}

    def update_task(self, new_task):
        task_id = new_task.id_
        if task_id not in self.stored_tasks:
            self.stored_tasks[task_id] = new_task
            return
        if self.stored_tasks[task_id].modified < new_task.modified:
            self.stored_tasks[task_id] = new_task

    def _fetch_edited(self):
        logger.info("fetching updates")
        p = params.using(after=self.lastedit)
        [pageinfo, *tasks] = self.api.tasks.get(p)
        assert pageinfo['num'] == pageinfo['total']
        logger.info("{}/{} fetched".format(pageinfo['num'], pageinfo['total']))
        for t in tasks:
            self.update_task(task_schema.load(t).data)
        self.lastedit = round(time.time())

    def _clean_deleted(self):
        logger.info("fetching deletes")
        [_, *del_tasks] = self.api.tasks.deleted()
        for t in del_tasks:
            key = t['id']
            if key in self.stored_tasks:
                del self.stored_tasks[key]
        self.lastdelete = round(time.time())

    def sync(self):
        acc = self.api.account.get()
        if acc['lastedit_task'] > self.lastedit:
            self._fetch_edited()

        if acc['lastdelete_task'] > self.lastdelete:
            self._clean_deleted()

    def get_tasks(self, sync=True):
        sync and self.sync()
        return self.stored_tasks

    def by_id(self, task_id, sync=True):
        return self.get_tasks(sync).get(int(task_id))


class ToodledoClient:
    def __init__(self, uid):
        self.user = ToodledoUser(uid)
        self.tasks = TaskCache(self.user)
        self.tasks.sync()
        self.msg_task_map = {}

    @property
    def auth_url(self):
        return self.user.session.auth_url

    def auth(self, url) -> bool:
        return self.user.session.authorize(url)

    def assoc_task_msg(self, msg_id, task_id):
        self.msg_task_map[msg_id] = task_id

    def get_by_msg_id(self, msg_id):
        tid = self.msg_task_map.get(msg_id)
        return tid and self.get_task_by_id(tid)

    def get_task_by_id(self, task_id):
        return self.tasks.by_id(task_id, False)

    def get_tasks(self, task_id=None, tag=None, comp=False, prior=None) -> [Task]:
        if task_id is not None:
            return maybe_list(self.get_task_by_id(task_id))

        filters = []
        if tag is not None:
            filters.append(lambda t: tag in t.tags)
        if comp is not None:
            filters.append(lambda t: t.completed() == comp)
        if prior is not None:
            if prior > 0:
                filters.append(lambda t: t.priority >= prior)
            else:
                filters.append(lambda t: t.priority == prior)

        tasks = self.tasks.get_tasks().values()
        filtered = filter(andf(*filters), tasks)
        duegetter = attrgetter('duedate', Inf())
        proirgetter = compose(lambda x: -x, attrgetter('priority'))
        return list(sorted(filtered, reverse=True, key=tuple_func(duegetter, proirgetter)))

    def edit_add_task(self, new_task):
        new_dump = [task_schema.dumps(new_task).data]
        if hasattr(new_task, 'id_'):
            [resp] = self.user.tasks.edit(params.using(tasks=new_dump))
        else:
            [resp] = self.user.tasks.add(params.using(tasks=new_dump))
        resp_task = task_schema.load(resp).data
        self.tasks.update_task(resp_task)
        return resp_task
