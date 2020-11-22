from utils.connectDb import database

def main():
        db = database()
        db.connect()
        print("I am just here to say casually Hi....So, Hi! Oh and This: \n")
        db.getVersion()
        db.getTestTableMeta()


if __name__ == "__main__":
    main()