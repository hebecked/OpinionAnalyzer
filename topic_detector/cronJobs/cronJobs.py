import pycron
import time
import os
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()


class CronJobs:

    def __init__(self):
        self.jobs = [
            {"schedule": '*/15 * * * *', "module": 'AnalyseArticles.py', "onInit": True},
            #{"schedule": '0 * * * *', "module": 'AnalyseArticles.py', "onInit": True}
        ]

    def cronInit(self):
        logger.info("CronJobs successfully initiated")
        analyis_modules_path = '/usr/src/app/analysisModules/'
        for job in self.jobs:
            if job["onInit"]:
                logger.info("Found job to fire on init: " + job["module"])
                logger.info("Init...")
                time.sleep(60)
                logger.info("Firing Module on init: " + job["module"])
                os.system('python3 -u ' + analyis_modules_path + job["module"])

        while True:
            for job in self.jobs:
                if pycron.is_now(job["schedule"]):
                    logger.info("Firing CronJob: " + job["module"])
                    os.system('python3 -u ' + analyis_modules_path + job["module"])
            time.sleep(60)
