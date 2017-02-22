from toodledobot.bot import ToodledoBot
import os
import locale
import logging

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

def main():
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    bot = ToodledoBot(os.environ['TELEGRAM_TOKEN'])
    bot.start()

if __name__ == '__main__':
    logger.info("Started...")
    main()
