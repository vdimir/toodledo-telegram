import telegram
from .helpers import parse_task

from toodledo_client import with_user
from .textformatter import HtmlTextFormater
from .decorators import *
import re
import logging
logger = logging.getLogger(__name__)


fmt = HtmlTextFormater()

@add_user_id
def start_handler(bot, update, uid=None):
    bot.sendMessage(chat_id=uid, text="Hello!\n"
                                      "Type /auth and follow instructions")


@not_authorized_wrapper
@add_user_id
def auth_handler(bot, update, args, uid=None):
    if len(args) == 0:
        text = "Please, send redirect url in command /auth <url>\n" \
               "Authorization url: {}\n"
        bot.sendMessage(chat_id=uid,
                        text=text.format(with_user(uid).auth_url),
                        disable_web_page_preview=True)
        return
    res = with_user(uid).auth(args[0])
    text = "Authorizing success!" if res else "Wrong authorizing data!"
    bot.sendMessage(chat_id=uid, text=text)


@not_authorized_wrapper
@add_user_id
def get_tasks_handler(bot, update, uid=None):
    msg = update.message.text
    tag = re.match('#(\w+)', msg)
    tag = tag and tag.group(1)
    tasks = with_user(uid).get_tasks(tag=tag)
    if len(tasks) == 0:
        bot.sendMessage(chat_id=uid, text="No such tasks",
                        parse_mode=telegram.ParseMode.HTML)

    keys = list(map(
        lambda t: telegram.InlineKeyboardButton(t.title, callback_data="taskmenu{}".format(t.id_)),
        tasks))
    markup = telegram.InlineKeyboardMarkup([keys])
    res = fmt.task_list_fmt(tasks)
    r = bot.sendMessage(chat_id=uid, text=res,
                        reply_markup=markup,
                        parse_mode=telegram.ParseMode.HTML)


@not_authorized_wrapper
@add_user_id
def task_menu_handler(bot: telegram.Bot, update, uid=None):
    tid = update.callback_query.data[8:]
    tasks = with_user(uid).get_tasks(only_id=tid)
    if len(tasks) != 1:
        bot.answer_callback_query(update.callback_query.id, "Error!")
        return
    task = tasks[0]
    text = fmt.task_fmt(tasks)
    keys = [telegram.InlineKeyboardButton("complete", callback_data="comptask{}".format(tid))]
    markup = telegram.InlineKeyboardMarkup([keys])
    bot.sendMessage(chat_id=uid, text=text, reply_markup=markup)
    bot.answer_callback_query(update.callback_query.id)


@not_authorized_wrapper
@add_user_id
def task_comp_handler(bot: telegram.Bot, update, uid=None):
    tid = update.callback_query.data[8:]
    res = with_user(uid).make_complete(tid)
    txt = "Ok" if res else "Error!"
    bot.answer_callback_query(update.callback_query.id, txt)


@not_authorized_wrapper
@add_user_id
def add_task_handler(bot, update, uid=None):
    msg = update.message.text
    task = parse_task(msg)
    if task is None:
        bot.sendMessage(chat_id=uid, text="Cannot parse :(")
        return
    res = with_user(uid).add_task(task)
    bot.sendMessage(chat_id=uid, text=res)


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
