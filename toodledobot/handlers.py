import telegram

from toodledoclient import toodledo_client
from .textformatter import HtmlTextFormater
from .decorators import *
from .actions import send_task_list, send_task
from .msg_parser import parse_add_task, parse_edit_task

import calendar
import re
import datetime
import logging

logger = logging.getLogger(__name__)

fmt = HtmlTextFormater()


@add_user_id
def start_handler(bot, update, uid=None):
    bot.sendMessage(chat_id=uid, text="Hello!\n"
                                      "Type /auth and follow instructions")


@add_user_id
def calendar_handler(bot, update, uid=None):
    today = datetime.date.today()
    (year, month, day) = today.year, today.month, today.day
    txt = calendar.TextCalendar().formatmonth(year, month, w=3)
    txt = txt.replace(' {} '.format(day), '[{}]'.format(day))
    bot.sendMessage(chat_id=uid, text="<pre>{}</pre>".format(txt),
                    parse_mode=telegram.ParseMode.HTML)


@not_authorized_wrapper
@add_user_id
def auth_handler(bot, update, args, uid=None):
    if len(args) == 0:
        text = "Please, send redirect url in command /auth <url>\n" \
               "Authorization url: {}\n"
        bot.sendMessage(chat_id=uid,
                        text=text.format(toodledo_client(uid).auth_url),
                        disable_web_page_preview=True)
        return
    res = toodledo_client(uid).auth(args[0])
    text = "Authorizing success!" if res else "Wrong authorizing data!"
    bot.sendMessage(chat_id=uid, text=text)


@not_authorized_wrapper
@add_user_id
def get_tasks_handler(bot, update, uid=None):
    tasks = toodledo_client(uid).get_tasks()
    send_task_list(bot, uid, tasks)


@not_authorized_wrapper
@add_user_id
def get_tasks_by_tag_handler(bot, update, uid=None, groups=None):
    tasks = toodledo_client(uid).get_tasks(tag=groups[0])
    if len(tasks) == 0:
        bot.sendMessage(chat_id=uid, text="<i>No such tasks</i>",
                        parse_mode=telegram.ParseMode.HTML)
        return
    send_task_list(bot, uid, tasks)


@user_error_wrapper
@not_authorized_wrapper
@add_user_id
def add_task_handler(bot, update, uid=None):
    msg = update.message.text
    task = parse_add_task(msg)
    res = toodledo_client(uid).edit_add_task(task)
    send_task(bot, uid, res)


@user_error_wrapper
@not_authorized_wrapper
@add_user_id
def task_edit_handler(bot: telegram.Bot, update, uid=None):
    msg_text = update.message.text
    mid = update.message.reply_to_message.message_id
    task = toodledo_client(uid).get_by_msg_id(mid)
    if task is None:
        raise UserInputError("Not found")

    edit_task = parse_edit_task(msg_text)
    if edit_task.get('comp'):
        edited_task = task.toggle_complete()
    elif edit_task.get('star'):
        s = not task.is_star()
        edited_task = task.using(star=s)
    elif edit_task.get('duedate'):
        edited_task = task.using(duedate=edit_task.get('duedate'))

    task = toodledo_client(uid).edit_add_task(edited_task)
    update.message.reply_to_message.edit_text(text=fmt.task_fmt(task),
                                              parse_mode=telegram.ParseMode.HTML)
    update.message.reply_text(text="Ok")


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
