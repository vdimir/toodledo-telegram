from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import MessageEntity

from toodledo import init_toodledo_client_app, NotAuthorizingError, User

import logging

import os

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
init_toodledo_client_app(os.environ['TOODLEDO_CLIENT_ID'],
                         os.environ['TOODLEDO_CLIENT_SECRET'])

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def auth(bot, update, args):
    url = args[0]
    uid = update.message.from_user.id
    r = User(uid).session.authorize(url)
    if r:
        bot.sendMessage(chat_id=update.message.chat_id, text="Authoring success!")
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong auth data!")


def get_tasks(bot, update):
    uid = update.message.from_user.id
    try:
        t = User(uid).tasks.get()
    except NotAuthorizingError:
        bot.sendMessage(chat_id=update.message.chat_id, text="Not authorized\n" +
                                                             User(uid).session.auth_url,
                        disable_web_page_preview=True)
        return
    d = str.join('\n', map(lambda t: t.title, t))
    bot.sendMessage(chat_id=update.message.chat_id, text=d)


def start(bot, update):
    uid = update.message.from_user.id
    bot.sendMessage(chat_id=update.message.chat_id, text="Authorize:\n" +
                                                         User(uid).session.auth_url,
                    disable_web_page_preview=True)


updater = Updater(token=TELEGRAM_TOKEN)
updater.dispatcher.add_handler(CommandHandler('auth', auth, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('list', get_tasks))

updater.start_polling()
