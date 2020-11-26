from datetime import date
from utils.connectDb import database
from random import randint
from time import sleep
import spiegel_scraper as spon
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S:')
logger = logging.getLogger()


def getFirstInitValue():
    db = database()
    db.connect()
    dateTuple = db.retrieveValues("SELECT is_first_init FROM general_data.system_configuration WHERE news_type = 'spiegel';")
    dateObject = []
    for item in dateTuple:
        dateObject.append(item[0])
    return dateObject


def setFirstInitValue(newsType, bool):
    db = database()
    db.connect()
    db.execute("UPDATE general_data.system_configuration SET is_first_init = " + bool + " WHERE news_type = '" + newsType + "';")


def getDateObject(start, end):
    db = database()
    db.connect()
    dateTuple = db.retrieveValues("SELECT date::VARCHAR FROM general_data.date_time_dimension WHERE date >= '" + start + "'  AND date <= '" + end + "';")
    dateObject = []
    for item in dateTuple:
        dateObject.append(item[0])
    return dateObject

def getYesterdayDateObject():
    db = database()
    db.connect()
    dateTuple = db.retrieveValues("SELECT date::VARCHAR FROM general_data.date_time_dimension WHERE date = CURRENT_DATE-'1 day'::INTERVAL;")
    dateObject = []
    for item in dateTuple:
        dateObject.append(item[0])
    return dateObject


def archive(year: int, month: int, day: int):
    html = spon.archive.html_by_date(date(year, month, day))
    content = spon.archive.scrape_html(html)
    return {'content': content, 'html': html}


def article(article_url):
    html = spon.article.html_by_url(article_url)
    content = spon.article.scrape_html(html)
    return {'content': content, 'html': html}


def article_comments(article_url):
    art=article(article_url)
    return spon.comments.by_article_id(art['content']['id'])


def createDbJson(rawData, date):
    return {
        "url": rawData["url"],
        "headline": rawData["headline"].replace("'", "").replace('"', ''),
        "published_at": date
    }


def insertData(tableName, values, dataLine):
    db = database()
    db.connect()
    db.execute("INSERT INTO " + tableName + " " + values + " VALUES ('" + dataLine["url"] + "'" + "," + "'" + dataLine["headline"] + "'" + "," + "'" + dataLine["published_at"] + "');")


if __name__ == '__main__':
    firstInitValue = getFirstInitValue()

    if firstInitValue[0]:
        dateObject = getDateObject('2020-11-01', '2020-11-24')
        setFirstInitValue('spiegel', 'false')

        for dateOt in dateObject:
            logger.info('Collecting Article meta data for day ' + dateOt)
            dateSplit = dateOt.split('-')
            year = int(dateSplit[0])
            month = int(dateSplit[1])
            day = int(dateSplit[2])
            archive_entries = spon.archive.by_date(date(year, month, day))

            for article in archive_entries:
                dbJson = createDbJson(article, dateOt)
                insertData('news_meta_data.articles', '(url, headline, published_at)', dbJson)
            sleep(randint(10, 100))
    else:
        dateObject = getYesterdayDateObject()

        for dateOt in dateObject:
            logger.info('Collecting Article meta data for day ' + dateOt)
            dateSplit = dateOt.split('-')
            year = int(dateSplit[0])
            month = int(dateSplit[1])
            day = int(dateSplit[2])
            archive_entries = spon.archive.by_date(date(year, month, day))

            for article in archive_entries:
                dbJson = createDbJson(article, dateOt)
                insertData('news_meta_data.articles', '(url, headline, published_at)', dbJson)
            sleep(randint(10, 100))


    #archive_entries = spon.achive.by_date(date(2020, 1, 31))
    #logger.info(archive_entries)
    #print(article("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8")["content"])
    #print(article_comments("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8"))
