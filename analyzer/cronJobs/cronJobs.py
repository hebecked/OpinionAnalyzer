import pycron
import time
import os
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()

class CronJobs:

    def __init__(self):
        self.jobs = [
            {"schedule": '0 0 * * *', "module": 'AnnalyseComments.py'}, #daily runs at midnight 
#            {"schedule": '@reboot', "module": 'AnnalyseComments.py'}, #run on reboot
            {"schedule": '0 1 * * *', "module": 'AnnalyseArticles.py'} #daily runs at 1 am
#            {"schedule": '@reboot', "module": 'AnnalyseArticles.py'} #run on reboot 
        ]

    def cronInit(self):
        logger.info("CronJobs successfully initiated")
        analyis_modules_path = '/usr/src/app/analysisModules/'
        while True:
            for job in self.jobs:
                if pycron.is_now(job["schedule"]):
                    logger.info("Firing CronJob: " + job["module"])
                    os.system('python3 -u ' + analyis_modules_path + job["module"])
            time.sleep(60)
