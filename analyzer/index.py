import utils
from utils import database
from cronJobs import CronJobs

def main():
    print('I am here to say hi!')

    db = database()
    db.connect()
    db.getVersion()
    db.getTestTableMeta()
    cron = CronJobs()
    cron.cronInit()


if __name__ == "__main__":
    main()
