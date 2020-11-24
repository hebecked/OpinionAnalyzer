from cronJobs.cronJobs import CronJobs
from time import sleep
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def main():
    logger.info("Analyzer successfully started")
    logger.info("Analyzer Scraper...")
    sleep(6)
    logger.info("Analyzer initiated")

    cron = CronJobs()
    cron.cronInit()


if __name__ == "__main__":
    main()
