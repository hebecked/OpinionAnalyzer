#!/usr/bin/python

from datetime import datetime, date, timedelta
import spiegel_scraper as spon
from utils.article import Article
from utils.comment import Comment
from utils.databaseExchange import DatabaseExchange
import dataCollectors.templateScraper
import time
import hashlib
import math


def calculate_commment_external_id(url, cmt: spon.comments) -> int:
    """
    calculate Comment external id as hash

    Parameters
    ----------
    url : TYPE
        Article url where the Comment has been found
    cmt : spon.comments
        spon.Comment object for which we calculate the external_id

    Returns
    -------
    external_id : int
        external_id as 8 byte integer

    """
    key = url + cmt['user']['username'] + cmt['body']
    external_id = int.from_bytes(hashlib.md5(key.encode()).digest()[0:8], "big", signed=True)
    return external_id


class SpiegelOnlineScraper(dataCollectors.templateScraper.Scraper):
    SUBSET_LENGTH = 10  # threshold for database flush
    DELAY_SUBSET = 1  # sleep x every SUBSET_LENGTH html requests
    DELAY_INDIVIDUAL = 0  # sleep x every html request

    def __init__(self):
        super(SpiegelOnlineScraper, self).__init__()
        self.id = 1  # set corresponding datasource id here
        self.has_errors = False
        pass

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
        date_list = [(timedelta(i) + date.today()) for i in range(num_of_days, 1)]
        full_list = []
        for dt in date_list:
            print("fetching date:", dt)
            try:
                full_list += (spon.archive.scrape_html(spon.archive.html_by_date(dt)))
            except:
                print("Article List crawl error!")
                self.has_errors = True
            time.sleep(SpiegelOnlineScraper.DELAY_INDIVIDUAL)  # remove Comment for crawler delay
        url_list = list(filter(lambda x: x['is_paid'] is False, full_list))  # remove paid articles without access
        for url in url_list:
            try:
                art = Article()
                art.setHeader(
                    {'source_date': url['date_published'].date(), 'source_id': self.id, 'url': str(url['url'])})
                article_return_list += [art]
            except:
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
            html = spon.article.html_by_url(art.getArticle()['header']['url'])
            content = spon.article.scrape_html(html)
        except:
            print("Article crawl error!")
            self.has_errors = True
            art.setObsolete(True)
            return False
        if 'id' in content.keys():
            art.setBody(
                {'headline': content['headline']['main'], 'body': content['text'], 'proc_timestamp': datetime.today(),
                 'proc_counter': 0})
            art.free_data = content['id']
        # add udfs
        if 'topics' in content.keys():
            for topic in content['topics']:
                art.addUdf('label', topic)
        if 'author' in content.keys():
            for author in content['author']['names']:
                art.addUdf('author', author)
        if 'date_created' in content.keys():
            art.addUdf('date_created', content['date_created'])
            try:
                art.setBodyCounter(max(
                    int(math.log((date.today() - date.fromisoformat(content['date_created'][0:10])).days * 24, 2)) - 1,
                    0))
            except:
                print('Body Counter not set')
        if 'date_modified' in content.keys():
            art.addUdf('date_modified', content['date_modified'])
        if 'date_published' in content.keys():
            art.addUdf('date_published', content['date_published'])
        return True

    def get_write_articles_details(self, writer: DatabaseExchange, article_list: list,
                                   start_date: date = date(1900, 1, 1)):
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
            for art in article_list[start_list_elem:(start_list_elem + SpiegelOnlineScraper.SUBSET_LENGTH)]:
                print("fetching Article:", art.getArticle()['header']['url'])
                self.get_article_details(art)
                time.sleep(SpiegelOnlineScraper.DELAY_INDIVIDUAL)
            writer.writeArticles(article_list[start_list_elem:(start_list_elem + SpiegelOnlineScraper.SUBSET_LENGTH)])
            for art in article_list[start_list_elem:(start_list_elem + SpiegelOnlineScraper.SUBSET_LENGTH)]:
                print("fetching comments for ", art.getArticle()['header']['url'])
                comment_list = self.get_comments_for_article(art, start_date)
                writer.writeComments(comment_list)
                time.sleep(SpiegelOnlineScraper.DELAY_INDIVIDUAL)
            start_list_elem += SpiegelOnlineScraper.SUBSET_LENGTH
            time.sleep(SpiegelOnlineScraper.DELAY_SUBSET)

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
            if cmt['body'] is not None and cmt['user'] is not None and cmt['created_at'] is not None:
                cmt_id = calculate_commment_external_id(art.getArticle()["header"]["url"], cmt)
                tmp_comment = Comment()
                tmp_comment.setData({"article_body_id": art.getBodyToWrite()["body"]["id"],
                                     "parent_id": parent_external_id, "level": comment_depth, "body": cmt['body'],
                                     "proc_timestamp": datetime.today(), "external_id": cmt_id})
                if 'user' in cmt.keys():
                    tmp_comment.addUdf("author", cmt['user']['username'])
                tmp_comment.addUdf("date_created", cmt['created_at'])
                if start_date <= date.fromisoformat(cmt['created_at'][0:10]) <= end_date:
                    comment_return_list += [tmp_comment]
                if 'replies' in cmt.keys():
                    tmp_comment.addUdf("replies", str(len(cmt['replies'])))
                    comment_return_list += self.flatten_comments(art, cmt['replies'], cmt_id, comment_depth + 1,
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
        if type(art.free_data) == str:
            article_id = art.free_data
        else:
            self.get_article_details(art)
            article_id = art.free_data
        try:
            comments = spon.comments.by_article_id(article_id)
            comment_return_list += self.flatten_comments(art, comments, None, 0, start_date, end_date)
        except:
            print("Comment crawl error!")
            self.has_errors = True
        return comment_return_list

    def __del__(self):
        pass


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting SpiegelOnlineScraper testcases here:\n\n")
    starttime = datetime.today()
    print("started at ", starttime)
    spiegel_online_scraper = SpiegelOnlineScraper()
    db = DatabaseExchange()
    db.logStartCrawl(spiegel_online_scraper.id)
    start = max(db.fetchLastRun(spiegel_online_scraper.id).date(), date(2020, 12, 22))
    end = date.today()
    article_header_list = spiegel_online_scraper.get_article_list(start, end)
    db.writeArticles(article_header_list)
    todo_list = db.fetchTodoListScraper(spiegel_online_scraper.id)
    spiegel_online_scraper.get_write_articles_details(db, todo_list)
    #   for art in todo_list:
    #       print("fetching comments for Article:",art)
    #       cmts=spiegel_online_scraper.getCommentsForArticle(art)
    #       db.writeComments(cmts)
    #       time.sleep(1)

    db.logEndCrawl(not spiegel_online_scraper.has_errors)
    print("Laufzeit= ", datetime.today() - starttime)
    db.close()
