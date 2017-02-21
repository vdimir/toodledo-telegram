from toodledobot.bot import ToodledoBot
import os
import locale


def main():
    locale.setlocale(locale.LC_TIME, "ru_RU")
    bot = ToodledoBot(os.environ['TELEGRAM_TOKEN'])
    bot.start()

if __name__ == '__main__':
    main()
