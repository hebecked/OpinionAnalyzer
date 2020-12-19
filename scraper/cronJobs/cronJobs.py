import pycron
import time
import os
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()

class CronJobs:

    def __init__(self):
        self.jobs = [
            #{"schedule": '* * * * *', "module": 'test.py'},  # Execute every minute "test.py"
            {"schedule": '* */24 * * *', "module": 'SpiegelOnlineScraper.py'},  # Execute every 30 minutes "spiegelCollector.py"
        ]

    def cronInit(self):
        logger.info("CronJobs successfully initiated")
        data_collectors_path = '/usr/src/app/dataCollectors/'
        while True:
            for job in self.jobs:
                if pycron.is_now(job["schedule"]):
                    logger.info("Firing CronJob: " + job["module"])
                    os.system('python3 -u ' + data_collectors_path + job["module"])
            time.sleep(60)
