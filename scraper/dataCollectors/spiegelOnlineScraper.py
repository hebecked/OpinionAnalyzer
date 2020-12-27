#!/usr/bin/python

import math
import time
from datetime import datetime, date, timedelta

import spiegel_scraper as spon

import dataCollectors.templateScraper
from utils.article import Article
from utils.comment import Comment
from utils.comment import calculate_comment_external_id
from utils.databaseExchange import DatabaseExchange


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
                art.set_header(
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
            html = spon.article.html_by_url(art.get_article()['header']['url'])
            content = spon.article.scrape_html(html)
        except:
            print("Article crawl error!")
            self.has_errors = True
            art.set_obsolete(True)
            return False
        if 'id' in content.keys():
            art.set_body(
                {'headline': content['headline']['main'], 'body': content['text'], 'proc_timestamp': datetime.today(),
                 'proc_counter': 0})
            art.free_data = content['id']
        # add udfs
        if 'topics' in content.keys():
            for topic in content['topics']:
                art.add_udf('label', topic)
        if 'author' in content.keys():
            for author in content['author']['names']:
                art.add_udf('author', author)
        if 'date_created' in content.keys():
            art.add_udf('date_created', content['date_created'])
            try:
                art.set_body_counter(max(
                    int(math.log((date.today() - date.fromisoformat(content['date_created'][0:10])).days * 24, 2)) - 1,
                    0))
            except:
                print('Body Counter not set')
        if 'date_modified' in content.keys():
            art.add_udf('date_modified', content['date_modified'])
        if 'date_published' in content.keys():
            art.add_udf('date_published', content['date_published'])
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
                print("fetching Article:", art.get_article()['header']['url'])
                self.get_article_details(art)
                time.sleep(SpiegelOnlineScraper.DELAY_INDIVIDUAL)
            writer.write_articles(article_list[start_list_elem:(start_list_elem + SpiegelOnlineScraper.SUBSET_LENGTH)])
            for art in article_list[start_list_elem:(start_list_elem + SpiegelOnlineScraper.SUBSET_LENGTH)]:
                print("fetching comments for ", art.get_article()['header']['url'])
                comment_list = self.get_comments_for_article(art, start_date)
                writer.write_comments(comment_list)
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
                cmt_ext_id = calculate_comment_external_id(
                    art.get_article()["header"]["url"], cmt['user']['username'], cmt['body']
                )
                tmp_comment = Comment()
                tmp_comment.set_data({"article_body_id": art.get_body_to_write()["body"]["id"],
                                      "parent_id": parent_external_id, "level": comment_depth, "body": cmt['body'],
                                      "proc_timestamp": datetime.today(), "external_id": cmt_ext_id})
                if 'user' in cmt.keys():
                    tmp_comment.add_udf("author", cmt['user']['username'])
                tmp_comment.add_udf("date_created", cmt['created_at'])
                if start_date <= date.fromisoformat(cmt['created_at'][0:10]) <= end_date:
                    comment_return_list += [tmp_comment]
                if 'replies' in cmt.keys():
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
    start_time = datetime.today()
    print("started at ", start_time)
    spiegel_online_scraper = SpiegelOnlineScraper()
    db = DatabaseExchange()
    db.log_scraper_start(spiegel_online_scraper.id)
    start = max(db.fetch_scraper_last_run(spiegel_online_scraper.id).date(), date(2020, 12, 20))
    end = date.today()
    article_header_list = spiegel_online_scraper.get_article_list(start, end)
    db.write_articles(article_header_list)
    todo_list = db.fetch_scraper_todo_list(spiegel_online_scraper.id)
    spiegel_online_scraper.get_write_articles_details(db, todo_list)
    #   for art in todo_list:
    #       print("fetching comments for Article:",art)
    #       cmts=spiegel_online_scraper.getCommentsForArticle(art)
    #       db.writeComments(cmts)
    #       time.sleep(1)

    db.log_scraper_end(not spiegel_online_scraper.has_errors)
    print("Laufzeit= ", datetime.today() - start_time)
    db.close()