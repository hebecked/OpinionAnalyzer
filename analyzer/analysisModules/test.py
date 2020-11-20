import utils
from utils import database


class test:

    def test(self):
        db = database()
        db.connect()
        print("I am just here to say casually Hi....So, Hi! Oh and This: \n")
        db.getVersion()
        db.getTestTableMeta()