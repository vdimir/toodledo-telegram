from toodledoclient.datatypes import Task
from .errors import UserInputError

import dateparser

from pyparsing import Word, ZeroOrMore, Optional, Suppress, ParseException
import pyparsing as prs

rus_alphas = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
alphas = prs.alphas + rus_alphas
alphanums = prs.alphanums + rus_alphas


def parse_date(due):
    return dateparser.parse(due, settings={'PREFER_DATES_FROM': 'future'}, languages=['en', 'ru']) or due


def parse_task(text):
    cmd = Suppress(Optional(prs.Word('/', prs.alphas)))
    title = (Word(alphanums + ' ,!')
             .setParseAction(lambda t: ('title', t.asList()[0].strip()))).setName('title')
    tags = (ZeroOrMore(Suppress('#') + Word(alphas))
            .setParseAction(lambda t: ('tags', t.asList())))
    due = Optional(Suppress('@') + Word(alphanums + ' ')
                   .setParseAction(lambda t: ('duedate', parse_date(t.asList()[0]))))

    task_parser = cmd + title + tags + due
    try:
        raw_task = dict(task_parser.parseString(text).asList())
    except ParseException as e:
        raise UserInputError(str(e))

    if isinstance(raw_task.get('duedate'), str):
        raise UserInputError("Invalid date: '{}'".format(raw_task.get('duedate')))

    return Task(**raw_task)
