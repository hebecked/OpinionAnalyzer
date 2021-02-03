#!/usr/bin/python

import math
import time
from datetime import datetime, date, timedelta
import pytz
import dataCollectors.templateScraper
from utils.article import Article
from utils.comment import Comment
from utils.comment import calculate_comment_external_id
from utils.databaseExchange import DatabaseExchange
from api.welt import Welt
import logging
import sys
import os
from multiprocessing import cpu_count, Pool
from contextlib import closing
import copy
import unicodedata
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


class WeltScraper(dataCollectors.templateScraper.Scraper):
    SUBSET_LENGTH = 10  # threshold for database flush
    DELAY_SUBSET = 1  # sleep x every SUBSET_LENGTH html requests
    DELAY_INDIVIDUAL = 0  # sleep x every html request
    RUN_THRESHOLD = 5

    def __init__(self):
        super(WeltScraper, self).__init__()
        self.id = 2  # set corresponding datasource id here
        self.has_errors = False
        self.api = Welt()

    def get_article_list(self, start_date: date = date(1900, 1, 1), end_date: date = date.today()) -> list:
        """
        function makes use of spiegel_scraper package to directly create own Article object from crawling the archive
                
        Parameters
        ----------
        start_date : date, optional
            The default is date(1900,1,1).
        end_date : date, optional
            The default is date.today().

        Returns
        -------
        article_return_list
            List of corresponding Article objects (published between start and end date) from this source \n
            Article will just contain header information so far
        """
        article_return_list = []
        num_of_days = (start_date - end_date).days
        date_list = [(timedelta(i) + end_date) for i in range(num_of_days, 1)]
        full_list = []
        for dt in date_list:
            logger.info("process-id "+str(os.getpid())+" fetching article list for date " + str(dt))
            try:
                as_datetime = datetime.combine(dt, datetime.min.time())
                url_list = self.api.get_all_articles_from_dates(as_datetime, as_datetime)
                for url in url_list:
                    full_list += [{'url': url, 'source_date': dt, 'is_paid': "/plus" in url}]
            except:
                logger.warning("process-id "+str(os.getpid())+" Article List crawl error!")
                self.has_errors = True
            time.sleep(WeltScraper.DELAY_SUBSET)  # remove Comment for crawler delay
        url_list = list(filter(lambda x: x['is_paid'] is False, full_list))  # remove paid articles without access
        for url in url_list:
            try:
                art = Article()
                art.set_header(
                    {'source_date': url['source_date'], 'source_id': self.id, 'url': str(url['url'])})
                article_return_list += [art]
            except:
                logger.warning("process-id "+str(os.getpid())+" Article incomplete: " + str(url))
                self.has_errors = True
        return article_return_list

    def get_article_details(self, art: Article) -> bool:
        """
        adds detailed information (article text and several others) to article \n
        Article body will be added

        Parameters
        ----------
        art : Article
            the Article to add detailed information to

        Returns
        -------
        bool
            returns True if successful.

        """
        try:
            welt_api_return = self.api.get_article_meta(art.get_article()['header']['url'])
        except:
            logger.warning("process-id "+str(os.getpid())+" Article crawl error fetching details: article url = "
                           + str(art.get_article()['header']['url']))
            self.has_errors = True
            art.set_obsolete(True)
            return False
        return_keys = welt_api_return.keys()
        if 'headline' in return_keys and 'articleBody' in return_keys:
            if not art.set_body(
                {'headline': unicodedata.normalize('NFKD', welt_api_return['headline'].replace("\n", ' ').replace("\t", ' ')),
                    'body': unicodedata.normalize('NFKD', welt_api_return['articleBody'].replace("\n", ' ').replace("\t", ' ')),
                    'proc_timestamp': datetime.now(pytz.timezone('Europe/Berlin'))}):
                art.set_obsolete(True)
                return False
        else:
            art.set_obsolete(True)
            return False
        # add udfs
        if 'author' in return_keys:
            art.add_udf('author',
                        unicodedata.normalize('NFKD',
                                            welt_api_return['author']['name'].replace("\n", ' ').replace("\t", ' ')))
        if 'dateModified' in return_keys:
            art.add_udf('date_modified', welt_api_return['dateModified'])
        if 'datePublished' in return_keys:
            art.add_udf('date_published', welt_api_return['datePublished'])
            try:
                art.set_body_counter(max(
                    int(math.log((date.today() -
                                  date.fromisoformat(welt_api_return['datePublished'][0:10])).days * 24, 2)) - 1, 0))
            except:
                # use default
                pass
        return True

    def get_write_articles_details(self, writer: DatabaseExchange, article_list: list,
                                   start_date: date = date(1900, 1, 1)) -> bool:
        """
        

        Parameters
        ----------
        writer : DatabaseExchange
            DatabaseExchange object, the crawler will use to connect to database
        article_list : list
            a list of articles to fetch details for and write to database
        start_date : date, optional
            used to define which comments are too old to be fetched. Comments posted after startdate will be processed. \n
            he default is date(1900,1,1).

        Returns
        -------
        None.

        """
        if type(article_list) != list:
            return False
        start_list_elem = 0
        while start_list_elem < len(article_list):
            for art in article_list[start_list_elem:(start_list_elem + WeltScraper.SUBSET_LENGTH)]:
                logger.info("process-id "+str(os.getpid())+" fetching article: " + str(art.get_article()['header']['url']))
                self.get_article_details(art)
                time.sleep(WeltScraper.DELAY_INDIVIDUAL)
            writer.write_articles(article_list[start_list_elem:(start_list_elem + WeltScraper.SUBSET_LENGTH)])
            fetch_comments_list = list(filter(lambda x:  x.is_in_db() and not x.get_article()['header']['obsolete'],
                                         article_list[start_list_elem:(start_list_elem + WeltScraper.SUBSET_LENGTH)]))
            for art in fetch_comments_list:
                logger.info("process-id "+str(os.getpid())+" fetching comments for " + str(art.get_article()['header']['url']))
                comment_list = self.get_comments_for_article(art, start_date)
                if comment_list:
                    writer.write_comments(comment_list)
                time.sleep(WeltScraper.DELAY_INDIVIDUAL)
            start_list_elem += WeltScraper.SUBSET_LENGTH
            time.sleep(WeltScraper.DELAY_SUBSET)
        return True

    def get_comments_for_article(self, art: Article, start_date: date = date(1900, 1, 1),
                                 end_date: date = date.today()) -> list:
        """
        

        Parameters
        ----------
        art : Article
            input Article for which we want to gather comments
        start_date : date, optional
             comments before this date are dropped. The default is date(1900,1,1).
        end_date : date, optional
            comments after this date are dropped. The default is date.today().

        Returns
        -------
        comment_return_list : list
            list of all Comment objects below the Article, which fit between the given dates


        """
        if 'id' not in art.get_body_to_write()["body"].keys():
            return []
        comment_return_list = []
        try:
            api_return = self.api.get_article_comments(art.get_article()['header']['url'])
            raw_comment_list = list(filter(lambda x: 'parentId' not in x.keys(), api_return))
        except:
            logger.warning("process-id "+str(os.getpid())+" Comment crawl error for article_id : " +
                           str(art.get_article()['header']['id']))
            raw_comment_list = []
            self.has_errors = True
        for cmt in raw_comment_list:
            if type(cmt) != dict:
                continue
            if cmt['contents'] is not None and cmt['user'] is not None and cmt['created'] is not None:
                cmt_ext_id = calculate_comment_external_id(
                    art.get_article()["header"]["url"], cmt['user']['displayName'], cmt['contents']
                )
                tmp_comment = Comment()
                if not tmp_comment.set_data({"article_body_id": art.get_body_to_write()["body"]["id"],
                                      "level": 0,
                                      "body": unicodedata.normalize('NFKD',
                                                                    cmt['contents'].replace("\n", ' ').replace("\t", ' ')),
                                      "proc_timestamp": datetime.now(pytz.timezone('Europe/Berlin')), "external_id": cmt_ext_id}):
                    continue
                if 'user' in cmt.keys():
                    tmp_comment.add_udf("author", unicodedata.normalize('NFKD', cmt['user']['displayName']))
                tmp_comment.add_udf("date_created", cmt['created'])
                if start_date <= date.fromisoformat(cmt['created'][0:10]) <= end_date:
                    comment_return_list += [tmp_comment]
                if 'childCount' in cmt.keys():
                    tmp_comment.add_udf("replies", cmt['childCount'])
        return comment_return_list

    def __del__(self):
        pass

    def wrap_get_write_articles_parallel(self, article_list: list,
                                       start_date: date = date(1900, 1, 1)) -> bool:
        db = DatabaseExchange()
        print("startrun")
        art = Article()
        cmt = Comment()
        self.get_write_articles_details(db, article_list, start_date)
        db.close()
        return True


def run_all():
    """
       full run of Scraper.
       Fetching all articles - starting today and moving backwards in chunks of one week
       will first add article-headers, then crawl bodies and comments
       restart with next (older) week
       
       running on cpu_count-1 cores at the same time to concurrently crawl the pages at faster pace

        Returns
        -------
        None
    """
    start_time = datetime.now(pytz.timezone('Europe/Berlin'))
    logger.info("full run step - started at " + str(start_time))
    welt_scraper = WeltScraper()
    db = DatabaseExchange()
    end_date = date.today()
    while True:
        db.log_scraper_start(welt_scraper.id)
        start_date = end_date - timedelta(weeks=1)
        article_header_list = welt_scraper.get_article_list(start_date, end_date)
        end_date = start_date - timedelta(1)
        if len(article_header_list) == 0:
            break
        db.write_articles(article_header_list)
        todo_list = db.fetch_scraper_todo_list(welt_scraper.id)
        if not todo_list:
            continue
        num_processes = min(cpu_count() - 1, 5)  # num processes reduced. IP-ban with 9 processes after about 1,5 hours
        chunk_size = math.ceil(len(todo_list) / num_processes)
        with closing(Pool(processes=num_processes)) as pool:
            result = [pool.apply_async(welt_scraper.wrap_get_write_articles_parallel,
                                       args=(copy.deepcopy(todo_list[i * chunk_size:(i + 1) * chunk_size]),))
                                       for i in range(0, num_processes)]
            _ = [p.get() for p in result]
        db.log_scraper_end(False)
        logger.info("full run step - duration = " + str(datetime.now(pytz.timezone('Europe/Berlin')) - start_time))
    db.close()


def run_regular():
    """
       Regular run of Scraper. Fetching new articles since last run or default date (if no complete run finished so far)

        Returns
        -------
        None
    """
    default_start_date = date.today() - timedelta(30)
    start_time = datetime.now(pytz.timezone('Europe/Berlin'))
    logger.info("regular run - started at " + str(start_time))
    welt_scraper = WeltScraper()
    db = DatabaseExchange()
    time_since_last_start = db.check_scraper_running(welt_scraper.id)
    if time_since_last_start < timedelta(hours=WeltScraper.RUN_THRESHOLD):
        db.close()
        logger.info("already running - exit without start ")
        return
    db.log_scraper_start(welt_scraper.id)
    start = max(db.fetch_scraper_last_run(welt_scraper.id).date(), default_start_date)
    end = date.today()
    article_header_list = welt_scraper.get_article_list(start, end)
    db.write_articles(article_header_list)
    end_historical = db.fetch_scraper_oldest(welt_scraper.id)
    start_historical = end_historical - timedelta(2)
    article_header_list = welt_scraper.get_article_list(start_historical, end_historical)
    db.write_articles(article_header_list)
    todo_list = db.fetch_scraper_todo_list(welt_scraper.id)
    welt_scraper.get_write_articles_details(db, todo_list)
    db.log_scraper_end(not welt_scraper.has_errors)
    logger.info("regular run - duration = " + str(datetime.now(pytz.timezone('Europe/Berlin')) - start_time))
    db.close()


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting WeltScraper testcases here:\n\n")
    logger.info("call parameters: " + str(sys.argv))
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            run_all()
        else:
            run_regular()
    else:
        run_regular()
    # welt_scraper = WeltScraper()
    # todo = welt_scraper.get_article_list(date(2020, 1, 10), date(2020, 1, 21))
    # cmts = []
    # print("todo: ", len(todo))
    # for i, t in enumerate(todo):
    #     print("crawling article", i)
    #     t.set_header_id(i+1)
    #     t.set_body_id(i+1)
    #     welt_scraper.get_article_details(t)
    #     cmts += welt_scraper.get_comments_for_article(t)
    # for t in todo[0:10]:
    #     t.print()
    # for c in cmts[0:10]:
    #     c.print()

