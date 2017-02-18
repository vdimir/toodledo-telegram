from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from datetime import date, datetime


class ToodledoDate(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return 0
        return datetime(year=value.year, month=value.month, day=value.day).timestamp()

    def _deserialize(self, value, attr, obj):
        if value == 0:
            return None
        return date.fromtimestamp(float(value))


class ToodledoDatetime(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return 0
        return value.timestamp()

    def _deserialize(self, value, attr, obj):
        if value == 0:
            return None
        return datetime.fromtimestamp(float(value))


class Task:
    def __init__(self, **data):
        for name, item in data.items():
            setattr(self, name, item)

    def __repr__(self):
        attributes = sorted(["{}={}".format(name, item) for name, item in self.__dict__.items()])
        return "<Task {}>".format(", ".join(attributes))

    def completed(self):
        return self.completed_date is not None


class TaskSchema(Schema):
    id_ = fields.Integer(dump_to="id", load_from="id")
    title = fields.String(validate=Length(max=255))
    completed_date = ToodledoDate(dump_to="completed", load_from="completed")

    @post_load
    def build(self, data):
        return Task(**data)


def create_task_list(data) -> [Task]:
    schema = TaskSchema()
    return [schema.load(x).data for x in data[1:]]


def data_processor(path, action):
    task_processors = {'get': create_task_list}
    processors = {'tasks': task_processors}
    return processors.get(path, {}).get(action)
