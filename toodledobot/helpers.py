from toodledoclient.datatypes import Task
import re

import dateparser


def parse_task(text):
    title = re.search('/add ([^#@]+)', text)
    if title is not None:
        title = title.group(1)
    else:
        return None

    tags = re.findall('#\w+', text)
    tags = list(map(lambda s: s[1:], tags))

    due = re.search('@[^#@]+', text)
    if due is not None:
        due = due.group()[1:].strip()
        due = dateparser.parse(due, settings={'PREFER_DATES_FROM': 'future'}, languages=['en', 'ru'])
    task = Task(title=title, tags=tags, duedate=due)
    return task
