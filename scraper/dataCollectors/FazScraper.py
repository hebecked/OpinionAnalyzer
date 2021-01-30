#!/usr/bin/python

import math
import time
from datetime import datetime, date, timedelta
import dataCollectors.templateScraper
from utils.article import Article
from utils.comment import Comment
from utils.comment import calculate_comment_external_id
from utils.databaseExchange import DatabaseExchange
from api.faz import Faz
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


class FazScraper(dataCollectors.templateScraper.Scraper):
    SUBSET_LENGTH = 10  # threshold for database flush
    DELAY_SUBSET = 1  # sleep x every SUBSET_LENGTH html requests
    DELAY_INDIVIDUAL = 0  # sleep x every html request

    def __init__(self):
        super(FazScraper, self).__init__()
        self.id = 3  # set corresponding datasource id here
        self.has_errors = False
        self.api = Faz()

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
                    full_list += [{'url': url, 'source_date': dt, 'is_paid': "/premiumContent" in url}]
            except:
                logger.warning("process-id "+str(os.getpid())+" Article List crawl error!")
                self.has_errors = True
            time.sleep(FazScraper.DELAY_SUBSET)  # remove Comment for crawler delay
        url_list = list(filter(lambda x: x['is_paid'] is False, full_list))
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
            faz_api_return = self.api.get_article_meta(art.get_article()['header']['url'])
        except:
            logger.warning("process-id "+str(os.getpid())+" Article crawl error fetching details: article url = "
                           + str(art.get_article()['header']['url']))
            self.has_errors = True
            art.set_obsolete(True)
            return False
        if 'article_meta' not in faz_api_return.keys() or 'article_body_meta' not in faz_api_return.keys():
            art.set_obsolete(True)
            self.has_errors = True
            return False
        header_keys = faz_api_return['article_meta'].keys()
        body_keys = faz_api_return['article_body_meta'].keys()
        if ('isAccessibleForFree' in body_keys and 'False' in
            faz_api_return['article_body_meta']['isAccessibleForFree'])\
                or ('article' in header_keys and 'type' in faz_api_return['article_meta']['article'].keys() and
                    'Bezahlartikel' in faz_api_return['article_meta']['article']['type']):
            art.set_obsolete(True)  # paid article can not be detected earlier
            return False
        if 'headline' in body_keys and 'articleBody' in body_keys:
            art.set_body(
                {'headline': unicodedata.normalize('NFKD',
                                                   faz_api_return['article_body_meta']['headline'].
                                                   replace("\n", ' ').replace("\t", ' ').strip()),
                 'body': unicodedata.normalize('NFKD',
                                               faz_api_return['article_body_meta']['articleBody'].
                                                   replace("\n", ' ').replace("\t", ' ').strip()),
                 'proc_timestamp': datetime.today(),
                 'proc_counter': 0})
        # add udfs
        if 'author' in body_keys:
            if type(faz_api_return['article_body_meta']['author']) == dict \
                    and 'name' in faz_api_return['article_body_meta']['author'].keys():
                art.add_udf('author', unicodedata.normalize('NFKD',
                                                            faz_api_return['article_body_meta']['author']['name'].
                                                   replace("\n", ' ').replace("\t", ' ').strip()))
            elif type(faz_api_return['article_body_meta']['author']) == list:
                for aut in faz_api_return['article_body_meta']['author']:
                    if type(aut) == dict and 'name' in aut.keys():
                        art.add_udf('author', unicodedata.normalize('NFKD', aut['name'].
                                                   replace("\n", ' ').replace("\t", ' ').strip()))

        if 'article' in header_keys and 'publishedFirst' in faz_api_return['article_meta']['article'].keys():
            art.add_udf('date_created', faz_api_return['article_meta']['article']['publishedFirst'])
            art.add_udf('date_published', faz_api_return['article_meta']['article']['publishedFirst'])
            try:
                art.set_body_counter(max(
                    int(math.log((date.today() -
                                  date.fromisoformat(faz_api_return
                                        ['article_meta']['article']['publishedFirst'][0:10])).days * 24, 2))
                    - 1, 0))
            except:
                # use default
                pass
        if 'dateModified' in body_keys:
            art.add_udf('date_modified', faz_api_return['article_body_meta']['dateModified'])
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
            for art in article_list[start_list_elem:(start_list_elem + FazScraper.SUBSET_LENGTH)]:
                logger.info("process-id "+str(os.getpid())+" fetching article: " + str(art.get_article()['header']['url']))
                self.get_article_details(art)
                time.sleep(FazScraper.DELAY_INDIVIDUAL)
            writer.write_articles(article_list[start_list_elem:(start_list_elem + FazScraper.SUBSET_LENGTH)])
            fetch_comments_list = list(filter(lambda x: not x.get_article()['header']['obsolete'],
                                         article_list[start_list_elem:(start_list_elem + FazScraper.SUBSET_LENGTH)]))
            for art in fetch_comments_list:
                logger.info("process-id "+str(os.getpid())+" fetching comments for " + str(art.get_article()['header']['url']))
                comment_list = self.get_comments_for_article(art, start_date)
                writer.write_comments(comment_list)
                time.sleep(FazScraper.DELAY_INDIVIDUAL)
            start_list_elem += FazScraper.SUBSET_LENGTH
            time.sleep(FazScraper.DELAY_SUBSET)
        return True

    def flatten_comments(self, art: Article, comment_list: list, parent_external_id: int = None, comment_depth=0,
                         start_date: date = date(1900, 1, 1), end_date: date = date.today()) -> list:
        """
        recursively traverses the Comment tree and returns list of own Comment objects filled with predefined data

        Parameters
        ----------
        art : Article
            the Article the comments belong to
        comment_list : list
            list of comments (starting level)
        parent_external_id : int, optional
            for recursive call: if Comment has parent, add parent_id here to save this connection to database \n
            The default is None.
        comment_depth : TYPE, optional
            current depth of Comment list. The default is starting value of 0 (Comment for Article).
        start_date : date, optional
            comments before this date are dropped. The default is date(1900,1,1).
        end_date : date, optional
            comments after this date are dropped. The default is date.today().

        Returns
        -------
        comment_return_list:list
            list of all Comment objects below the Article, which fit between the given dates

        """
        comment_return_list = []
        if type(comment_list) != list:
            return []
        for cmt in comment_list:
            if type(cmt) != dict:
                continue
            cmt_keys = cmt.keys()
            if 'body' in cmt_keys and 'title' in cmt_keys and 'author' in cmt_keys and 'created_at' in cmt_keys and \
                    cmt['body'] is not None and cmt['title'] is not None and cmt['author'] is not None \
                    and cmt['created_at'] is not None:
                cmt_ext_id = calculate_comment_external_id(
                    art.get_article()["header"]["url"], cmt['author'],
                    unicodedata.normalize('NFKD', cmt['title'] + " " + cmt['body'])
                )
                tmp_comment = Comment()
                tmp_comment.set_data({"article_body_id": art.get_body_to_write()["body"]["id"],
                                      "parent_id": parent_external_id, "level": comment_depth,
                                      "body": unicodedata.normalize('NFKD', cmt['title'] + " " + cmt['body']),
                                      "proc_timestamp": datetime.today(), "external_id": cmt_ext_id})
                tmp_comment.add_udf("headline", cmt['title'])
                tmp_comment.add_udf("author", cmt['author'])
                tmp_comment.add_udf("date_created", cmt['created_at'])
                if start_date <= date.fromisoformat(cmt['created_at'][0:10]) <= end_date:
                    comment_return_list += [tmp_comment]
                if 'replies' in cmt_keys:
                    tmp_comment.add_udf("replies", str(len(cmt['replies'])))
                    comment_return_list += self.flatten_comments(art, cmt['replies'], cmt_ext_id, comment_depth + 1,
                                                                 start_date, end_date)
        return comment_return_list

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
        comment_return_list = []
        try:
            comments = self.api.get_article_comments(art.get_article()['header']['url'])
            comment_return_list += self.flatten_comments(art, comments, None, 0, start_date, end_date)
        except:
            logger.warning("process-id "+str(os.getpid())+" Comment crawl error for article_id : "
                           + str(art.get_article()['header']['id']))
            self.has_errors = True
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
    start_time = datetime.today()
    logger.info("full run step - started at " + str(start_time))
    spiegel_online_scraper = FazScraper()
    db = DatabaseExchange()
    end_date = date.today()
    while True:
        db.log_scraper_start(spiegel_online_scraper.id)
        start_date = end_date - timedelta(weeks=1)
        article_header_list = spiegel_online_scraper.get_article_list(start_date, end_date)
        end_date = start_date - timedelta(1)
        if len(article_header_list) == 0:
            break
        db.write_articles(article_header_list)
        todo_list = db.fetch_scraper_todo_list(spiegel_online_scraper.id)
        if not todo_list:
            continue
        num_processes = min(cpu_count() - 1, 5)  # num processes reduced. IP-ban with 9 processes after about 1,5 hours
        chunk_size = math.ceil(len(todo_list) / num_processes)
        with closing(Pool(processes=num_processes)) as pool:
            result = [pool.apply_async(spiegel_online_scraper.wrap_get_write_articles_parallel,
                                       args=(copy.deepcopy(todo_list[i * chunk_size:(i + 1) * chunk_size]),))
                                       for i in range(0, num_processes)]
            _ = [p.get() for p in result]
        db.log_scraper_end(False)
        logger.info("full run step - duration = " + str(datetime.today() - start_time))
    db.close()


def run_regular():
    """
       Regular run of Scraper. Fetching new articles since last run or default date (if no complete run finished so far)

        Returns
        -------
        None
    """
    default_start_date = date.today() - timedelta(20)
    start_time = datetime.today()
    logger.info("regular run - started at " + str(start_time))
    faz_scraper = FazScraper()
    db = DatabaseExchange()
    db.log_scraper_start(faz_scraper.id)
    start = max(db.fetch_scraper_last_run(faz_scraper.id).date(), default_start_date)
    end = date.today()
    article_header_list = faz_scraper.get_article_list(start, end)
    db.write_articles(article_header_list)
    todo_list = db.fetch_scraper_todo_list(faz_scraper.id)
    faz_scraper.get_write_articles_details(db, todo_list, start - timedelta(1))
    db.log_scraper_end(not faz_scraper.has_errors)
    logger.info("regular run - duration = " + str(datetime.today() - start_time))
    db.close()


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting FazScraper testcases here:\n\n")
    logger.info("call parameters: " + str(sys.argv))
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            run_all()
        else:
            run_regular()
    else:
        run_regular()
    # faz_scraper = FazScraper()
    # start_time = datetime.today()
    # todo = faz_scraper.get_article_list(date(2021, 1, 21), date(2021, 1, 21))
    # cmts = []
    # print("num articles: ", len(todo))
    # for i, t in enumerate(todo):
    #     print("crawling article", i)
    #     t.set_header_id(i+1)
    #     t.set_body_id(i+1)
    #     faz_scraper.get_article_details(t)
    #     cmts += faz_scraper.get_comments_for_article(t)
    # print("time of run: " + str(datetime.today() - start_time))
    # for t in todo[0:10]:
    #     t.print()
    # for c in cmts[0:10]:
    #     c.print()


