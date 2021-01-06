from cronJobs.cronJobs import CronJobs
from time import sleep
from utils.connectDb import Database
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def main():
    logger.info("Analyzer successfully started.")
    logger.info("Testing database connection.")
    db = Database()
    db.connect()
    db.getVersion()
    db.getTestTableMeta()
    logger.info("Initiating Analyzer...")
    sleep(6)
    #test sentiment.py, topicDetection.py etc.
    logger.info("Analyzer initiated")

    cron = CronJobs()
    cron.cronInit()


if __name__ == "__main__":
    main()
