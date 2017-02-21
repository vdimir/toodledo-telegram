
class Task:
    def __init__(self, title=None, id_=None, modified=0, tags=None, completed_date=None, duedate=None, **kwargs):
        self.modified = modified
        self.id_ = id_
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
