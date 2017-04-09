import telegram

from toodledoclient import toodledo_client
from .textformatter import HtmlTextFormater
from .decorators import *
from .actions import send_task_list, send_task, send_text
from .msg_parser import parse_add_task, parse_edit_task, parse_prior_search

import calendar
import re
import datetime
import logging

from database import NotifiedUsers
notified_users = NotifiedUsers()

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
        raise UserInputError("No such tasks")
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

    edit_task = parse_edit_task(task, msg_text)
    task = toodledo_client(uid).edit_add_task(edit_task)
    update.message.reply_to_message.edit_text(text=fmt.task_fmt(task),
                                              parse_mode=telegram.ParseMode.HTML)
    update.message.reply_text(text="<i>Edited!</i>", parse_mode=telegram.ParseMode.HTML)


@user_error_wrapper
@not_authorized_wrapper
@add_user_id
def other_handler(bot: telegram.Bot, update, uid=None):
    msg_text = update.message.text
    priority = parse_prior_search(msg_text)
    if priority is None:
        raise UserInputError("Unknown command: {}".format(msg_text))

    tasks = toodledo_client(uid).get_tasks(prior=priority)
    if len(tasks) == 0:
        raise UserInputError("No such tasks")
    send_task_list(bot, uid, tasks)


def tasks_mailing_job(bot, job):
    logger.info("Execute schedule task")

    for uid in notified_users.get_notified():
        tasks = toodledo_client(uid).get_tasks(days_left=3)
        if len(tasks) == 0:
            send_text(bot, uid, "<i>Your daily is empty</i>")
            continue
        send_text(bot, uid, "<i>Your daily:</i>")
        send_task_list(bot, uid, tasks)
        logger.info("send tasks for %d" % uid)


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
