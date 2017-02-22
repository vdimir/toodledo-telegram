from telegram.ext import CommandHandler, Updater, CallbackQueryHandler

from .handlers import *

# реплаи
# инлайн клавиатура
# кастомная клавиатура

class ToodledoBot:
    def __init__(self, telegram_token):
        self.updater = Updater(token=telegram_token)

    def start(self):
        self.setup_handlers()
        self.updater.start_polling()

    def setup_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', start_handler))
        dispatcher.add_handler(CommandHandler('auth', auth_handler, pass_args=True))
        dispatcher.add_handler(CommandHandler('list', get_tasks_handler))
        dispatcher.add_handler(CommandHandler('add', add_task_handler))
        dispatcher.add_handler(CallbackQueryHandler(task_menu_handler, pattern='taskmenu\d+'))
        dispatcher.add_handler(CallbackQueryHandler(task_comp_handler, pattern='comptask\d+'))
        dispatcher.add_error_handler(error_handler)
