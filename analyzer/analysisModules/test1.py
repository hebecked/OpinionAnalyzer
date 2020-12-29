from utils.connectDb import Database


def main():
        db = Database()
        db.connect()
        print("I am just here to say casually Hi....So, Hi! Oh and This: \n")
        db.getVersion()
        db.getTestTableMeta()


if __name__ == "__main__":
    main()