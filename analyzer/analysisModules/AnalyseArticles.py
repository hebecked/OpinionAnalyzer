from utils.connectDb import Database
import json

def main():
    db = Database()
    db.connect()
    print("I am just here to say casually Hi....So, Hi! Oh and This: \n")
    db.getVersion()
    db.getTestTableMeta()


if __name__ == "__main__":
    with open('../Testdata/TestArticle.json') as f:
        testArticle = json.load(f)
        #dict_keys(['url', 'id', 'channel', 'subchannel', 'headline', 'intro', 'text', 'topics', 'author', 'comments_enabled', 'date_created', 'date_modified', 'date_published', 'breadcrumbs'])
        # main()