import telegram

from toodledo_client import with_user, task_str
from utils import unlines


def add_user_id(func):
    def wrapped(bot, update, *args, **kwargs):
        uid = update.message.from_user.id
        res = func(bot, update, *args, uid=uid, **kwargs)
        return res
    return wrapped


@add_user_id
def auth_handler(bot, update, args, uid=None):
    res = with_user(uid).auth(args[0])
    text = "Authorizing success!" if res else "Wrong auth data!"
    bot.sendMessage(chat_id=update.message.chat_id, text=text)


@add_user_id
def get_tasks_handler(bot, update, uid=None):
    tasks = with_user(uid).get_tasks()
    keys = list(map(
        lambda t: telegram.InlineKeyboardButton(t.title, callback_data="taskmenu{}".format(t.id_)),
        tasks))
    markup = telegram.InlineKeyboardMarkup([keys])
    res = unlines(tasks, task_str)
    r = bot.sendMessage(chat_id=update.message.chat_id, text=res,
                        reply_markup=markup,
                        parse_mode=telegram.ParseMode.HTML)


def task_menu_handler(bot: telegram.Bot, update):
    cq = update.callback_query
    uid = cq.from_user.id
    tid = cq.data[8:]
    tasks = with_user(uid).get_tasks(only_id=tid)
    if len(tasks) != 1:
        bot.answer_callback_query(cq.id, "Error!")
        return
    task = tasks[0]
    text = task_str(task)
    keys = [telegram.InlineKeyboardButton("complete", callback_data="comptask{}".format(tid))]
    markup = telegram.InlineKeyboardMarkup([keys])
    bot.sendMessage(chat_id=uid, text=text, reply_markup=markup)
    bot.answer_callback_query(cq.id)


def task_comp_handler(bot: telegram.Bot, update):
    cq = update.callback_query
    uid = cq.from_user.id
    tid = cq.data[8:]
    res = with_user(uid).make_complete(tid)
    txt = "Ok" if res else "Error!"
    bot.answer_callback_query(cq.id, txt)


@add_user_id
def add_task_handler(bot, update, args, uid=None):
    pass