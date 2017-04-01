from datetime import date


def persistent(names=None):
    if names is None:
        names = []
    if not isinstance(names, list):
        names = [names]

    class Persistent:
        persist_fields = names

        def __init__(self, **kwargs):
            for name, item in kwargs.items():
                setattr(self, name, item)

        def using(self, **kwargs):
            for name in self.persist_fields:
                if name not in kwargs and hasattr(self, name):
                    kwargs[name] = getattr(self, name)
            return self.__class__(**kwargs)
    return Persistent


class Task(persistent('id_')):
    def __init__(self, id_=None, **kwargs):
        super().__init__(**kwargs)
        if id_ is not None:
            self.id_ = id_

    def __repr__(self):
        attributes = sorted(["{}={}".format(name, item) for name, item in self.__dict__.items()])
        return "<{} {}>".format(self.__class__.__name__, ", ".join(attributes))

    def toggle_complete(self):
        completed_date = date.today() if not self.completed() else None
        return self.using(completed_date=completed_date)

    def completed(self):
        return self.completed_date is not None
