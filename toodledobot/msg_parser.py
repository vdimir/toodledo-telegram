from toodledoclient.datatypes import Task
from .errors import UserInputError

import dateparser

from pyparsing import Word, OneOrMore, Optional, Suppress, ParseException, Literal
import pyparsing as prs

rus_alphas = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
alphas = prs.alphas + rus_alphas
alphanums = prs.alphanums + rus_alphas


def parse_date(due):
    return dateparser.parse(due, settings={'PREFER_DATES_FROM': 'future'}, languages=['en', 'ru']) or due


due_parser = (Suppress('$') + Word(alphanums + ' ')
              .setParseAction(lambda t: ('duedate', parse_date(t.asList()[0])))).setName('$due')

tag_pars = (Suppress('#') + Word(alphas))

tags = (OneOrMore(tag_pars)
        .setParseAction(lambda t: ('tags', t.asList()))).setName('tags')

pn = Literal('?').setParseAction(lambda _: ('priority', -1))
p0 = Literal('0').setParseAction(lambda _: ('priority', 0))
p1 = Literal('!').setParseAction(lambda _: ('priority', 1))
p2 = Literal('!!').setParseAction(lambda _: ('priority', 2))
p3 = Literal('!!!').setParseAction(lambda _: ('priority', 3))
prior_parser = (p3 | p2 | p1 | p0 | pn).setName('priority')


def parse_add_task(text):
    cmd = Suppress(Optional(prs.Word('/', prs.alphas)))
    title = (Word(alphanums + ' ,')
             .setParseAction(lambda t: ('title', t.asList()[0].strip()))).setName('title')

    task_parser = cmd + title + Optional(prior_parser) + Optional(tags) + Optional(due_parser)
    try:
        raw_task = dict(task_parser.parseString(text).asList())
    except ParseException as e:
        raise UserInputError(str(e))

    if isinstance(raw_task.get('duedate'), str):
        raise UserInputError("Invalid date: '{}'".format(raw_task.get('duedate')))

    return Task(**raw_task)


def parse_edit_task(task, text):
    comp = (Literal('/comp') | Literal('comp')
            | Literal('done') | Literal('X') | Literal('x')).setParseAction(lambda _: ('comp', True)).setName('/comp')
    star = (Literal('/star') | Literal('star')).setParseAction(lambda _: ('star', True)).setName('/star')
    due_none_parser = Literal('$$').setParseAction(lambda t: ('duedate', None))
    task_parser = comp | star | (due_parser | due_none_parser) | prior_parser | tags
    try:
        edit_task = dict(task_parser.parseString(text.lower()).asList())
    except ParseException as e:
        raise UserInputError(str(e))

    if edit_task.get('comp') is not None:
        edited_task = task.toggle_complete()
    elif edit_task.get('star') is not None:
        s = not task.is_star()
        edited_task = task.using(star=s)
    elif edit_task.get('tags') is not None:
        edit_task['tags'] += task.tags
        edited_task = task.using(**edit_task)
    else:
        edited_task = task.using(**edit_task)

    return edited_task


def parse_prior_search(text):
    try:
        prior = dict(prior_parser.parseString(text).asList())
    except ParseException as e:
        prior = {'priority': None}
    return prior['priority']
