
class Task:
    def __init__(self, title, tags=None, completed_date=None, duedate=None, **kwargs):
        self.title = title
        self.completed_date = completed_date
        self.duedate = duedate
        self.tags = [] if tags is None else tags

    def __repr__(self):
        attributes = sorted(["{}={}".format(name, item) for name, item in self.__dict__.items()])
        return "<Task {}>".format(", ".join(attributes))

    @property
    def completed(self):
        return self.completed_date is not None

    def __str__(self):
        x = '[x]' if self.completed else '[ ]'
        due = '' if self.duedate is None else self.duedate.strftime("<i>%d %b, %A</i>")
        return str.format("{x} {title} {due}", x=x, title=self.title, due=due)


class TaskList:
    def __init__(self, tasks):
        self.tasks = tasks
        self.need_completed = False

    def _predicate(self, t):
        vals = [not t.completed or self.need_completed]
        return all(vals)

    def get(self):
        return filter(self._predicate, self.tasks)

    def __str__(self):
        return str.join("\n", map(str, self.get()))

