from crontab import CronTab


class cronJobs:

    def __init__(self):
        """ initalize class and get connection parameters """
        self.jobs = [
            {"schedule": '* * * * *', "module": 'test.py'}  # Execute every minute "test.py"
        ]

    def cronInit(self):
        cron = CronTab(tabfile='/usr/src/app/cronJobs/crontab')
        job = cron.new(command='echo hello_world')
        job.minute.every(1)
        cron.write()

