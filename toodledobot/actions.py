import telegram

from toodledoclient import toodledo_client

from .textformatter import HtmlTextFormater
fmt = HtmlTextFormater()


def send_task(bot, uid, task):
    res = fmt.task_fmt(task)
    r = bot.sendMessage(chat_id=uid, text=res,
                        parse_mode=telegram.ParseMode.HTML)
    toodledo_client(uid).assoc_task_msg(r['message_id'], task.id_)


def send_task_list(bot, uid, tasks):
    for task in tasks:
        send_task(bot, uid, task)
