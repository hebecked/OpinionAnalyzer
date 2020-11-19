import utils
from utils import database

if __name__ == '__main__':
    db = database()
    db.connect()
    db.getVersion()
    db.getTestTableMeta()