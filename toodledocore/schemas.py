from marshmallow import Schema, fields, post_load
from marshmallow.validate import Length

from datetime import date, datetime


class ToodledoDate(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return 0
        return datetime(year=value.year, month=value.month, day=value.day, hour=12).timestamp()

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
    __model__ = None

    id_ = fields.Integer(dump_to="id", load_from="id")
    title = fields.String(validate=Length(max=255))
    completed_date = ToodledoDate(dump_to="completed", load_from="completed")
    duedate = ToodledoDate(dump_to="duedate", load_from="duedate")
    tags = ToodledoTags(dump_to="tag", load_from="tag")
    context = fields.Integer()
    ref = fields.Integer()
    modified = fields.Integer(load_only=True)
    star = fields.Boolean()
    note = fields.String(validate=Length(max=32000))

    @post_load
    def build(self, data):
        if self.__model__ is None:
            return data
        return self.__model__(**data)
