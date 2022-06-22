import os
import schedule

from time import sleep
from dotenv import load_dotenv

from utils.telegram import TelegramBot

from src.database import DataStorage
from src.bots.bot_99freela import send_99freela
from src.bots.freelancer_com import send_freelancer_com
from src.bots.toogit import send_toogit
from src.bots.upwork import send_upwork


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, '.env'))
job_storage = DataStorage()
FILTERS = ["bot", "robo", "scrapper", "robô", "robot", "telegram", "crawler", "scrap", "scrapy", "beautifulsoap",  "raspagem", "raspagem", "extração", "web-scrapping", "web-crawling"]

REMOTE = True
HEADLESS = True


def main():
    """
    send freela jobs to telegram
    """
    print('> iniciando robô...', end="\n")
    telegram = TelegramBot(ROOT_DIR)

    print('> extraíndo trabalhos...')
    send_99freela(telegram, {'filters':FILTERS} ,job_storage)
    send_toogit(telegram, job_storage, FILTERS)
    send_freelancer_com(telegram, FILTERS, job_storage)
    send_upwork(telegram, job_storage, FILTERS, HEADLESS, REMOTE)


if __name__ == "__main__":
    # main()
    main_hour =  os.environ.get('POST_HOUR') #"12:00"
    schedule.every().monday.at(main_hour).do(main)
    schedule.every().wednesday.at(main_hour).do(main)
    schedule.every().friday.at(main_hour).do(main)

    while True:
        schedule.run_pending()
        print('Listening...', end="\r")
        sleep(1)
    