from cronJobs.cronJobs import CronJobs
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def main():
    logger.info("Analyzer successfully initiated")

    cron = CronJobs()
    cron.cronInit()


if __name__ == "__main__":
    main()
