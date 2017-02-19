from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from datetime import date, datetime

from .datatypes import Task


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


class ToodledoTags(fields.Field):
    def _serialize(self, value, attr, obj):
        assert isinstance(value, list)
        return ", ".join(sorted(value))

    def _deserialize(self, value, attr, obj):
        assert isinstance(value, str)
        if value == "":
            return []
        return [x.strip() for x in value.split(",")]


class TaskSchema(Schema):
    id_ = fields.Integer(dump_to="id", load_from="id")
    title = fields.String(required=True, validate=Length(max=255))
    completed_date = ToodledoDate(dump_to="completed", load_from="completed")
    duedate = ToodledoDate(dump_to="duedate", load_from="duedate")
    tags = ToodledoTags(dump_to="tag", load_from="tag", missing='[]')
    context = fields.Integer()
    ref = fields.Integer()

    @post_load
    def build(self, data):
        return Task(**data)


def task_get_processor(data):
    return TaskSchema(many=True).load(data[1:]).data


def result_processor(path, action):
    task_processors = {'get': task_get_processor}
    processors = {'tasks': task_processors}
    return processors.get(path, {}).get(action)


def task_add_processor(data):
    if not isinstance(data, list):
        data = [data]
    return {
        "tasks": TaskSchema(many=True).dumps(data).data
    }

def params_processor(path, action):
    task_processors = {'add': task_add_processor}
    processors = {'tasks': task_processors}
    return processors.get(path, {}).get(action)
