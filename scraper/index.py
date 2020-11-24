from cronJobs.cronJobs import CronJobs
from utils.connectDb import database
from time import sleep
import os
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def getFirstInitValue():
    db = database()
    db.connect()
    dateTuple = db.retrieveValues("SELECT is_first_init FROM general_data.system_configuration WHERE news_type = 'spiegel';")
    dateObject = []
    for item in dateTuple:
        dateObject.append(item[0])
    return dateObject

def main():
    logger.info("Scraper successfully started")
    logger.info("Initiating Scraper...")
    sleep(6)
    logger.info("Scraper initiated")
    firstInitValue = getFirstInitValue()
    if firstInitValue[0]:
        logger.info('No original Init found for Spiegel Scraper')
        logger.info('Triggering Spiegel Scraper')
        os.system('python3 -u /usr/src/app/dataCollectors/getSPON.py')

    cron = CronJobs()
    cron.cronInit()


if __name__ == "__main__":
    main()
