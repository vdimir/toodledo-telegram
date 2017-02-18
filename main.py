from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import MessageEntity

from user import *
from toodledo import *

import logging


import os
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
init_toodledo_client_app(os.environ['TOODLEDO_CLIENT_ID'],
                          os.environ['TOODLEDO_CLIENT_SECRET'])

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def auth(bot, update, args=None):
    if args is None:
        url = update.message.text
    else:
        url = args[0]
    uid = update.message.from_user.id
    user(uid).session.authorize(url)


def get_tasks(bot, update):
    uid = update.message.from_user.id
    try:
        t = user(uid).tasks.get()
    except NotAuthorizingError:
        bot.sendMessage(chat_id=update.message.chat_id, text="Not authorized\n" +
                                                             user(uid).session.auth_url,
                        disable_web_page_preview=True)
        return

    bot.sendMessage(chat_id=update.message.chat_id, text=t)


def start(bot, update):
    uid = update.message.from_user.id
    bot.sendMessage(chat_id=update.message.chat_id, text="Authorize:\n" +
                                                         user(uid).session.auth_url,
                    disable_web_page_preview=True)

updater = Updater(token=TELEGRAM_TOKEN)
text_url_filter = Filters.text & (Filters.entity(MessageEntity.URL) |
                                  Filters.entity(MessageEntity.TEXT_LINK))

updater.dispatcher.add_handler(MessageHandler(text_url_filter, auth))
updater.dispatcher.add_handler(CommandHandler('auth', auth, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('list', get_tasks))

updater.start_polling()
