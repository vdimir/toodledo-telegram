from toodledoclient.datatypes import Task
from itertools import count, repeat
from datetime import date

def unlines(arr, elem_str=str):
    return str.join('\n', map(elem_str, arr))


class HtmlTextFormater:
    def __init__(self):
        self.comp_sign = '\U00002611'
        self.uncomp_sign = '\U000025FD'
        self.star_sign = '\U00002B50'
        self._settings = {'note': True}

    def set(self, **kwargs):
        for k, v in kwargs:
            self._settings[k] = v
        return self

    def is_set(self, val):
        return self._settings.get(val, False)

    @staticmethod
    def tag_map(tag):
        # tmap = {'edu': '\U0001F4D2'}
        tmap = {}
        return tmap.get(tag, '#' + tag)

    def due_format(self, duedate):
        if duedate is None:
            return ''
        if duedate.year != date.today().year:
            return duedate.strftime("<i>%d %b %Y</i>")
        return duedate.strftime("<i>%d %b, %A</i>")

    def addnl(self, val):
        return val and '\n'+val

    def tags_format(self, tags):
        return ', '.join(map(self.tag_map, tags))

    def note_format(self, note):
        if self.is_set('note'):
            return note
        return ''

    def prior_format(self, prior):
        bages = ['\U00002754', '', '\U00002755', '\U0000203C', '\U0001F525']
        return bages[prior+1]

    def task_fmt(self, task=None, num=None):
        text = str.format("{num}{star}{comp}<b>{title}</b>{prior}{due}{note}{tags}",
                          num=num or '',
                          title=task.title,
                          star=task.star and self.star_sign or '',
                          comp=task.completed() and self.comp_sign or '',
                          prior=self.prior_format(task.priority),
                          due=self.addnl(self.due_format(task.duedate)),
                          tags=self.addnl(self.tags_format(task.tags)),
                          note=self.addnl(self.note_format(task.note)))
        return text
