import pycron
import time


class CronJobs:

    def cronInit(self):
        while True:
            if pycron.is_now('* * * * *'):  # True Every minute
                print('running nothing, because I am stupid (please kill me)')
                time.sleep(60)  # The process should take at least 60 sec
                # to avoid running twice or more in one minute
            else:
                time.sleep(15)


"""
    def __init__(self):
        self.jobs = [
            {"schedule": '* * * * *', "module": 'test.py'}  # Execute every minute "test.py"
        ]
"""