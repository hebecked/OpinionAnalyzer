import utils
from utils import database
#from cronJobs import cronJobs
import time
from flask import Flask

app = Flask(__name__)

app.run(host='0.0.0.0', port=8081)

def main():

    # regular test
    db = database()
    db.connect()
    db.getVersion()
    db.getTestTableMeta()
    print('I am here')


if __name__ == "__main__":
    main()
