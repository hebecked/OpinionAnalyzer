# -*- coding: utf-8 -*-

# todo: open tasks marked with todo

import datetime as dt
import pytz

import utils.connectDb as connectDb
from utils.article import Article
from utils.comment import Comment


class DatabaseExchange(connectDb.Database):
    SUBSET_LENGTH = 100  # threshold for database flush
    ANALYZER_RESULT_DEFAULT_COLUMNS = ['id', 'comment_id', 'analyzer_log_id']

    # class variable representing database architecture for analyzers
    __analyzer_database_structure = {}

    # class variables representing current logfile state in db
    __analyzer_ids = {}
    __scraper_log_id = None

    # database queries
    # scraper related database queries
    __SQL_SCRAPER_FETCH_LAST_RUN = """
                                      SELECT 
                                        MAX(start_timestamp) 
                                      FROM 
                                        news_meta_data.crawl_log 
                                      WHERE 
                                        success = True 
                                        AND source_id = %s;
                                   """

    __SQL_SCRAPER_CHECK_RUNNING = """
                                    SELECT
                                        start_timestamp,
                                        end_timestamp
                                    FROM
                                         news_meta_data.crawl_log
                                    WHERE
                                        source_id = %s
                                    ORDER BY id desc
                                    FETCH FIRST 1 ROW ONLY;
                                    """

    __SQL_SCRAPER_FETCH_TODO = """
                                  SELECT 
                                    article_id, 
                                    url, 
                                    article_body_id, 
                                    headline, 
                                    body, 
                                    proc_timestamp, 
                                    proc_counter 
                                  FROM 
                                    news_meta_data.v_todo_crawl
                                  WHERE 
                                    src_id = %s;
                               """

    __SQL_SCRAPER_FETCH_OLDEST = """
                                    SELECT 
                                        MIN(source_date)
                                    FROM
                                        news_meta_data.article_header
                                    WHERE
                                        source_id = %s;
                                """

    __SQL_SCRAPER_LOG_START = """
                                 INSERT INTO 
                                   news_meta_data.crawl_log (source_id, start_timestamp, success) 
                                 VALUES (%s, %s, False);
                              """

    __SQL_SCRAPER_LOG_END = """
                               UPDATE 
                                 news_meta_data.crawl_log 
                               SET 
                                 end_timestamp = %s, 
                                 success = %s 
                               WHERE id = %s;
                            """

    __SQL_SCRAPER_FETCH_MAX_LOG_ID = """
                                        SELECT 
                                          MAX(id) 
                                        FROM 
                                          news_meta_data.crawl_log 
                                        WHERE 
                                          source_id = %s;
                                     """

    # Article related database queries
    __SQL_ARTICLE_HEADER_FETCH_START_ID = """
                                             SELECT 
                                               MAX(id) 
                                             FROM 
                                               news_meta_data.article_header;
                                          """

    __SQL_ARTICLE_HEADER_INSERT = """
                                     INSERT INTO 
                                       news_meta_data.article_header (source_date, obsolete, source_id, url) 
                                     VALUES (%s, %s, %s, %s) 
                                     ON CONFLICT DO NOTHING;
                                  """

    __SQL_ARTICLE_HEADER_SET_OBSOLETE = """
                                        UPDATE 
                                            news_meta_data.article_header
                                        SET
                                            obsolete = true
                                        WHERE 
                                            id = %s;
                                    """

    __SQL_ARTICLE_HEADER_FETCH_ID = """
                                       SELECT 
                                         url, 
                                         id 
                                       FROM 
                                         news_meta_data.article_header 
                                       WHERE 
                                         id > %s 
                                         AND source_id = %s 
                                         AND source_date = %s;
                                    """

    __SQL_ARTICLE_BODY_FETCH_START_ID = """
                                           SELECT 
                                             MAX(id) 
                                           FROM 
                                             news_meta_data.article_body;
                                        """

    __SQL_ARTICLE_BODY_INSERT = """
                                   INSERT INTO 
                                     news_meta_data.article_body (article_id, headline, body, proc_timestamp, proc_counter) 
                                   VALUES (%s, %s, %s, %s, %s) 
                                   ON CONFLICT DO NOTHING;
                                """

    __SQL_ARTICLE_BODY_UPDATE = """
                                   UPDATE 
                                     news_meta_data.article_body 
                                   SET 
                                     proc_counter = %s 
                                   WHERE 
                                     id = %s;
                                """

    __SQL_ARTICLE_BODY_FETCH_ID = """
                                     SELECT 
                                       article_id, 
                                       MAX(id) AS id 
                                     FROM  
                                       news_meta_data.article_body 
                                     WHERE 
                                       id > %s 
                                     GROUP BY 
                                       article_id;
                                  """

    # udf related database queries
    __SQL_UDF_INSERT = """
                          INSERT INTO 
                            news_meta_data.udf_values (udf_id, object_type, object_id, udf_value) 
                          VALUES (%s, %s, %s, %s) 
                          ON CONFLICT DO NOTHING;
                       """

    # Comment related database queries
    __SQL_COMMENT_FETCH_START_ID = """
                                      SELECT 
                                        MAX(id) 
                                      FROM 
                                        news_meta_data.comment;
                                   """

    __SQL_COMMENT_INSERT = """
                              INSERT INTO 
                                news_meta_data.Comment (article_body_id, external_id, parent_id, level, body,proc_timestamp) 
                              VALUES (%s, %s, %s, %s, %s, %s) 
                              ON CONFLICT DO NOTHING;
                           """

    __SQL_COMMENT_FETCH_ID = """
                                SELECT 
                                  external_id, 
                                  article_body_id, 
                                  id 
                                FROM 
                                  news_meta_data.comment 
                                WHERE 
                                  id > %s 
                                  AND article_body_id IN %s;
                             """

    # todo get recent comments from view (by source_id and proc_timestamp)

    # analyzer related database queries
    __SQL_ANALYZER_FETCH_HEADER = """
                                     SELECT 
                                       id, 
                                       analyzer_view_name, 
                                       analyzer_table_name 
                                     FROM 
                                       news_meta_data.analyzer_header;
                                  """

    __SQL_ANALYZER_FETCH_TODO = """
                                   SELECT 
                                     comment_id, 
                                     comment_body 
                                   FROM 
                                     news_meta_data.{}
                                """  # {} needed to add data not wrapped in ''

    __SQL_ANALYZER_LOG_START = """
                                  INSERT INTO 
                                    news_meta_data.analyzer_log (analyzer_id, comment_id, start_timestamp) 
                                  VALUES (%s, %s, %s);
                               """

    __SQL_ANALYZER_FETCH_LOG_IDs = """
                                      SELECT 
                                        comment_id, 
                                        MAX(id) AS id  
                                      FROM 
                                        news_meta_data.analyzer_log 
                                      WHERE 
                                        start_timestamp = %s 
                                        AND analyzer_id = %s 
                                        AND comment_id IN %s 
                                      GROUP BY 
                                        comment_id;
                                   """

    __SQL_ANALYZER_FETCH_TARGET_COLUMNS = """
                                             SELECT 
                                               column_name 
                                             FROM 
                                               information_schema.columns 
                                             WHERE 
                                               table_schema = 'news_meta_data' 
                                               AND table_name = %s;
                                          """

    __SQL_ANALYZER_LOG_END = """
                                UPDATE 
                                  news_meta_data.analyzer_log 
                                SET 
                                  end_timestamp = %s, 
                                  success=True 
                                WHERE 
                                  id = %s 
                                  AND comment_id = %s;
                             """

    __SQL_ANALYZER_INSERT_RESULT = """
                                      INSERT INTO 
                                        news_meta_data.{} {} 
                                      VALUES %s;
                                   """  # {} needed to add data not wrapped in ''

    __SQL_TOPICIZER_FETCH_TODO = """
                                    SELECT 
                                        b.id, 
                                        b.body, 
                                        b.headline, 
                                        u.udf_value 
                                    FROM 
                                        news_meta_data.article_body as b,
                                        news_meta_data.udf_values as u
                                    WHERE
                                        b.id=u.object_id
                                        AND u.object_type=1
                                        AND u.udf_id=2
                                        AND NOT b.body=''
                                    FETCH FIRST 1000 ROWS ONLY;
                                    """  # rewrite with VIEW

    def __init__(self):
        super().__init__()
        print("initializing database exchange...")
        self.connect()
        print("connected")
        DatabaseExchange.__analyzer_database_structure = self.__fetch_analyzer_tables()
#        print("Analyzer tables: ", DatabaseExchange.__analyzer_database_structure)

    def close(self):
        super().close()

    def __del__(self):
        super().__del__()

    def connect(self):
        super().connect()

    def fetch_topicizer_data(self) -> dict:
        """
        fetches topic builder related data from database

        Returns
        -------
        dict
            { article_body_id : {body: str, headline : str, topics : list[str]} }

        """
        # todo all provisorical - rework later!
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_TOPICIZER_FETCH_TODO)
        result = cur.fetchall()
        cur.close()
        if len(result) == 0:
            return {}
        topicizer_data = {}
        for res in result:
            if res[0] in topicizer_data.keys():
                topicizer_data[res[0]]['topics'].append(res[3])
            else:
                topicizer_data[res[0]] = {'body': res[1], 'headline': res[2], 'topics': [res[3]]}
        return topicizer_data

    def __fetch_analyzer_tables(self) -> dict:
        """
        fetches all analyzer related table information from news_meta_data.analyzer_header \n
        in detail: view from which to crate the to do list and target table

        Returns
        -------
        dict
            { analyzer_id : {analyzer_view_name: str, analyzer_table_name : str} }

        """
        # fetch table data for analyzers from header table (which view and target table to use)
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_ANALYZER_FETCH_HEADER)
        result = cur.fetchall()  # id, analyzer_view_name, analyzer_table_name
        cur.close()
        if len(result) == 0:
            return {}
        analyzer_dict = {}
        for res in result:
            analyzer_dict[res[0]] = {'analyzer_view_name': res[1], 'analyzer_table_name': res[2]}
        return analyzer_dict

    def fetch_analyzer_todo_list(self, analyzer_id: int) -> list:
        """
        

        Parameters
        ----------
        analyzer_id : int
            analyzer unique id corresponding to id in analyzer_header table

        Returns
        -------
        list
            list of tuples (comment_id, comment_body) \n
            retrieved from corresponding analyzer related t do list (view)

        """
        if analyzer_id not in DatabaseExchange.__analyzer_database_structure.keys():
            return []
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_ANALYZER_FETCH_TODO.format(
                DatabaseExchange.__analyzer_database_structure[analyzer_id]['analyzer_view_name']
            )
        )
        result = cur.fetchall()  # comment_id, comment_body
        cur.close()
        data_set = set([])
        for res in result:
            data_set |= {res}
        todo_list = list(data_set)
        if not todo_list:
            return todo_list
        self.__log_analyzer_start(analyzer_id, list(c[0] for c in todo_list))
        return todo_list

    def __log_analyzer_start(self, analyzer_id: int, comment_id_list: list):
        """
        writes logging entry for all comment_id in list (analyzer_todo_list) to analyzer_log table

        Parameters
        ----------
        analyzer_id : int
            analyzer unique id corresponding to id in analyzer_header table
        comment_id_list : list
            list of comment_id (int)

        Returns
        -------
        bool
            True if successful

        """
        if analyzer_id not in DatabaseExchange.__analyzer_database_structure.keys():
            return False
        self.__analyzer_start_timestamp = dt.datetime.now(pytz.timezone('Europe/Berlin'))
        cur = self.conn.cursor()
        for comment_id in comment_id_list:
            cur.execute(
                DatabaseExchange.__SQL_ANALYZER_LOG_START,
                (analyzer_id, comment_id, self.__analyzer_start_timestamp)
            )
        DatabaseExchange.__analyzer_ids.update(
            self.__fetch_analyzer_log_ids(analyzer_id, comment_id_list)
        )
        self.conn.commit()
        cur.close()

    def __fetch_analyzer_log_ids(self, analyzer_id: int, comment_id_list: list) -> dict:
        """
        retrieve all logging ids in database table analyzer_log and save in class variable

        Parameters
        ----------
        analyzer_id : int
            analyzer unique id corresponding to id in analyzer_header table
        comment_id_list : list
            list of comment ids (int)

        Returns
        -------
        dict
            mapping table for comment_id to log_id as dict\n
             {comment_id : analyzer_log.id}

        """
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_ANALYZER_FETCH_LOG_IDs,
            (self.__analyzer_start_timestamp, analyzer_id, tuple(comment_id_list))
        )
        ids = cur.fetchall()
        cur.close()
        if len(ids) == 0:
            return {}
        return dict(ids)

    def __fetch_analyzer_columns(self, analyzer_id: int) -> list:
        """
        retrieving list of feasible target table column for given analyzer

        Parameters
        ----------
        analyzer_id : int
            analyzer unique id corresponding to id in analyzer_header table

        Returns
        -------
        list
            list of individual database columns in analyzer result table\n
            default columns excluded

        """
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_ANALYZER_FETCH_TARGET_COLUMNS,
            (DatabaseExchange.__analyzer_database_structure[analyzer_id]['analyzer_table_name'],)
        )
        table_fields = cur.fetchall()  # column_name for result table
        if len(table_fields) == 0:
            cur.close()
            return []
        columns = set(f[0] for f in table_fields) - set(DatabaseExchange.ANALYZER_RESULT_DEFAULT_COLUMNS)
        cur.close()
        return list(columns)

    def write_analyzer_results(self, analyzer_id: int, analyzer_result: list) -> bool:
        """
        writes analyzer result data to corresponding database result table (specified by analyzer_id)

        Parameters
        ----------
        analyzer_id : int
            analyzer unique id corresponding to id in analyzer_header table
        analyzer_result : list
            list of result dicts\n
            {database_column : analyzer_result}

        Returns
        -------
        bool
            True if successful

        """
        if not type(analyzer_result) == list:
            return False
        if analyzer_id not in DatabaseExchange.__analyzer_database_structure.keys():
            return False
        analyzer_end_timestamp = dt.datetime.now(pytz.timezone('Europe/Berlin'))
        target_columns = self.__fetch_analyzer_columns(analyzer_id)
        cols = tuple(DatabaseExchange.ANALYZER_RESULT_DEFAULT_COLUMNS[1:] + target_columns)
        columns_as_string = '(' + ','.join(cols) + ')'
        cur = self.conn.cursor()
        for result in analyzer_result:
            if not type(result) == dict:
                continue
            insert_sql = DatabaseExchange.__SQL_ANALYZER_INSERT_RESULT.format(
                DatabaseExchange.__analyzer_database_structure[analyzer_id]['analyzer_table_name'],
                columns_as_string
            )  # needed to fill data to sql statement without being wrapped as string ('')
            values = (result['comment_id'], DatabaseExchange.__analyzer_ids[result['comment_id']])
            if not (set(target_columns) - set(result.keys())):  # if set of missing columns are empty
                for col in target_columns:
                    values += tuple([result[col]])
                insert_sql.format(values)  # needed to fill data to sql statement without being wrapped as string ('')
                cur.execute(insert_sql, (values,))  # values tuple added to insert query
                cur.execute(
                    DatabaseExchange.__SQL_ANALYZER_LOG_END,
                    (analyzer_end_timestamp, DatabaseExchange.__analyzer_ids[result['comment_id']],
                        result['comment_id'])
                )
        self.conn.commit()
        cur.close()
        keys = DatabaseExchange.__analyzer_ids.keys()
        for result in analyzer_result:
            if result['comment_id'] in keys:
                del DatabaseExchange.__analyzer_ids[result['comment_id']]
        return True

    def fetch_scraper_todo_list(self, source_id: int) -> list:
        """
        get to do Article list from database for scraper specified by source_id

        Parameters
        ----------
        source_id : int
            scraper unique id corresponding to id in source_header table

        Returns
        -------
        list
            list of Article objects as saved in database\n
            retrieved from v_todo_crawl view for corresponding scraper source_id

        """
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_SCRAPER_FETCH_TODO,
            (source_id,)
        )
        result = cur.fetchall()  # article_id, url, article_body_id, headline, body, proc_timestamp, proc_counter
        cur.close()
        if len(result) == 0:
            return []
        todo_list = []
        for res in result:
            art = Article()
            art.set_header({'id': res[0], 'url': res[1], 'source_id': source_id})
            if res[2] is not None:
                art.set_body(
                    {'id': res[2], 'article_id': res[0], 'headline': res[3], 'body': res[4], 'proc_timestamp': res[5],
                     'proc_counter': res[6]})
                art.set_body_old()
            todo_list += [art]
        return todo_list

    def fetch_scraper_oldest(self, source_id: int) -> dt.datetime:
        """
        Parameters
        ----------
        source_id : int
            scraper unique id corresponding to id in source_header table

        Returns
        -------
        TYPE
            datetime.date object for the oldest source date in article_header table for this scraper

        """
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_SCRAPER_FETCH_OLDEST,
            (source_id,)
        )
        result = cur.fetchall()  # last timestamp of successful run
        cur.close()
        if result is None or result[0] is None or result[0][0] is None:
            return dt.datetime.now(pytz.timezone('Europe/Berlin'))
        return result[0][0]

    def fetch_scraper_last_run(self, source_id: int) -> dt.datetime:
        """

        Parameters
        ----------
        source_id : int
            scraper unique id corresponding to id in source_header table

        Returns
        -------
        TYPE
            datetime.datetime object for the last run of this scraper

        """
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_SCRAPER_FETCH_LAST_RUN,
            (source_id,)
        )
        result = cur.fetchall()  # last timestamp of successful run
        cur.close()
        if result is None or result[0] is None or result[0][0] is None:
            return dt.datetime(1990, 1, 1)
        return result[0][0]

    def check_scraper_running(self, source_id: int) -> dt.timedelta:
        """

        Parameters
        ----------
        source_id : int
            scraper unique id corresponding to id in source_header table

        Returns
        -------
        TYPE
            datetime.timedelta object for the time after the last start of this scraper

        """
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SQL_SCRAPER_CHECK_RUNNING,
            (source_id,)
        )
        result = cur.fetchall()  # last timestamp of successful run
        cur.close()

        if result is None or result[0] is None or result[0][0] is None:
            return dt.timedelta(days=1000)
        if result[0][1] is None:
            return dt.datetime.now(pytz.timezone('Europe/Berlin')) - result[0][0]
        return dt.timedelta(1000)

    def log_scraper_start(self, source_id: int) -> bool:
        """
        writes new line to crawl_log table\n
        start entry for scraper given by source_id

        Parameters
        ----------
        source_id : int
            scraper unique id corresponding to id in source_header table

        Returns
        -------
        bool
            True if successful

        """
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_SCRAPER_LOG_START,
                    (source_id, dt.datetime.now(pytz.timezone('Europe/Berlin'))))
        self.conn.commit()
        cur.execute(DatabaseExchange.__SQL_SCRAPER_FETCH_MAX_LOG_ID, (source_id,))
        result = cur.fetchall()  # id of last successful run
        cur.close()
        if result is None or result[0] is None or result[0][0] is None:
            return False
        DatabaseExchange.__scraper_log_id = result[0][0]
#        print("logId: ", DatabaseExchange.__scraper_log_id)
        return True

    def log_scraper_end(self, success: bool = True):
        """
        completes entry for current scraper run (adding end date and flag successful)

        Parameters
        ----------
        success : bool, optional
            Has crawling been successful? The default is True.

        Returns
        -------
        None.

        """
        cur = self.conn.cursor()
        update_tuple = (
            dt.datetime.now(pytz.timezone('Europe/Berlin')), success, DatabaseExchange.__scraper_log_id
        )
        cur.execute(
            DatabaseExchange.__SQL_SCRAPER_LOG_END,
            update_tuple
        )
        self.conn.commit()
        cur.close()

    def __fetch_article_ids(self, articles_list: list, start_id: int) -> dict:
        """
        fetches mapping of urls to article_id (given by database) from article_header table

        Parameters
        ----------
        articles_list : list
            list of Article objects
        start_id : int
            database id from which to start the extraction\n
            smallest possible id range for less traffic and response time

        Returns
        -------
        dict
            mapping table for url to article_id as dict\n
             {url : article_header.id}

        """
        article_ids = []
        cur = self.conn.cursor()
        for source_dates in set(
                (x.get_article()["header"]["source_id"], x.get_article()["header"]["source_date"])
                for x in articles_list):
            cur.execute(
                DatabaseExchange.__SQL_ARTICLE_HEADER_FETCH_ID,
                tuple([start_id] + list(source_dates))
            )
            result = cur.fetchall()  # url, article_id
            article_ids += list(result)
        cur.close()
        return dict(article_ids)

    def __fetch_body_ids(self, start_id: int) -> dict:
        """
        fetches mapping of article_id to latest body_id (given by database) from article_body table

        Parameters
        ----------
        start_id : int
            database id from which to start the extraction\n
            smallest possible id range for less traffic and response time
        Returns
        -------
        dict
            mapping table for article_id to body_id as dict\n
             {article_id : article_body.id}

        """
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_ARTICLE_BODY_FETCH_ID, (start_id,))
        result = cur.fetchall()  # article_id, body_id
        if len(result) == 0:
            return {}
        body_ids = list(result)
        return dict(body_ids)

    def __set_articles_obsolete(self, article_list: list):
        """
        sets column obsolete = True in article_header table for all articles in article_list

        Parameters
        ----------
        article_list
            list of articles to mark as obsolete in database
        """
        cur = self.conn.cursor()
        for art in article_list:
            cur.execute(DatabaseExchange.__SQL_ARTICLE_HEADER_SET_OBSOLETE, (art.get_article()['header']['id'],))
        self.conn.commit()
        cur.close()

    def __write_article_headers(self, article_list: list):
        """
        writes header data for Article objects in article_list to article_header table

        Parameters
        ----------
        article_list : list
            list of Article objects to be written to database

        Returns
        -------
        None.

        """
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_ARTICLE_HEADER_FETCH_START_ID)
        result = cur.fetchall()  # last header id before current insert run
        if result is None or result[0] is None or result[0][0] is None:
            start_id = 0
        else:
            start_id = result[0][0]  # todo check if correct
        for art in article_list:
            if art.set_header_complete():
                hdr = art.get_article()["header"]
                cur.execute(
                    DatabaseExchange.__SQL_ARTICLE_HEADER_INSERT,
                    (hdr["source_date"], hdr["obsolete"], hdr["source_id"], hdr["url"])
                )
        self.conn.commit()
        cur.close()
        self.__fill_header_ids(article_list, start_id)

    def __write_article_bodies(self, article_list: list):
        """
        writes article body data for Article objects in article_list to article_body table

        Parameters
        ----------
        article_list : list
            list of Article objects to be written to database

        Returns
        -------
        None.

        """
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_ARTICLE_BODY_FETCH_START_ID)
        result = cur.fetchall()  # last body id before current insert run
        if result is None or result[0] is None or result[0][0] is None:
            start_id = 0
        else:
            start_id = result[0][0]   # todo check if correct
        for art in article_list:
            if art.set_body_complete():
                body_to_use = art.get_body_to_write()
                if body_to_use["insert"]:
                    cur.execute(DatabaseExchange.__SQL_ARTICLE_BODY_INSERT, (
                        body_to_use["body"]["article_id"], body_to_use["body"]["headline"], body_to_use["body"]["body"],
                        body_to_use["body"]["proc_timestamp"], body_to_use["body"]["proc_counter"] + 1))
                else:
                    cur.execute(DatabaseExchange.__SQL_ARTICLE_BODY_UPDATE,
                                (body_to_use["body"]["proc_counter"] + 1, body_to_use["body"]["id"]))
        self.conn.commit()
        cur.close()
        self.__fill_body_ids(article_list, start_id)

    def __write_article_udfs(self, article_list: list):
        """
        writes udfs for Article objects in article_list to udf_values table

        Parameters
        ----------
        article_list : list
            list of Article objects to be written to database

        Returns
        -------
        None.

        """
        cur = self.conn.cursor()
        for art in article_list:
            if art.get_body_to_write()["insert"] and 'id' in art.get_article()["body"].keys():
                for udf in art.get_article()["udfs"]:
                    cur.execute(
                        DatabaseExchange.__SQL_UDF_INSERT,
                        (udf[0], Article.OBJECT_TYPE, art.get_article()["body"]["id"], udf[1])
                    )
        self.conn.commit()
        cur.close()

    def __fill_header_ids(self, article_list: list, start_id: int):
        """
        add database given article_id to Article object (after writing to database)

        Parameters
        ----------
        article_list : list
            list of Article objects to enrich with article_id\n
            (adding information to input list)
        start_id : int
            database id from which to start the extraction\n
            smallest possible id range for less traffic and response time

        Returns
        -------
        None.

        """
        id_lookup_dict = self.__fetch_article_ids(article_list, start_id)
        for art in article_list:
            url = art.get_article()["header"]["url"]
            if url in id_lookup_dict.keys():
                art.set_header_id(id_lookup_dict[url])

    def __fill_body_ids(self, article_list: list, start_id: int):
        """
        add database given body_id to Article object (after writing to database)

        Parameters
        ----------
        article_list : list
            list of Article objects to enrich with body_id\n
            (adding information to input list)
        start_id : int
            database id from which to start the extraction\n
            smallest possible id range for less traffic and response time

        Returns
        -------
        None.

        """
        id_lookup_dict = self.__fetch_body_ids(start_id)
        for art in article_list:
            article_id = art.get_article()["header"]["id"]
            if article_id in id_lookup_dict.keys():
                art.set_body_id(id_lookup_dict[article_id])

    def write_articles(self, article_list: list) -> bool:
        """
        write full Article objects from list (header, body, udfs) to database

        Parameters
        ----------
        article_list : list
            list of Article objects to ewrite to database

        Returns
        -------
        bool
            True if successful

        """
        if type(article_list) != list:
            return False
        start = 0
        return_value = True  # todo add error handling
        while start < len(article_list):
            work_list = list(
                filter(lambda x: type(x) == Article,
                       article_list[start:start + DatabaseExchange.SUBSET_LENGTH]))
            obsolete = list(filter(lambda x:  x.is_in_db() and x.get_article()['header']['obsolete'], work_list))
            self.__set_articles_obsolete(obsolete)
            headers = list(filter(lambda x: not (x.is_in_db()), work_list))
            self.__write_article_headers(headers)
#            print("Article headers written and id added") # todo delete line (debugging purposes only)
            bodies = list(filter(lambda x: x.is_in_db(), work_list))
            self.__write_article_bodies(bodies)
#            print("Article bodies written and id added") # todo delete line (debugging purposes only)
            bodies = list(filter(lambda x: x.is_in_db() and not x.get_article()['header']['obsolete'], work_list))
            self.__write_article_udfs(bodies)
#            print("Article udfs written") # todo delete line (debugging purposes only)
            start += DatabaseExchange.SUBSET_LENGTH
        return return_value

    def __fetch_comment_ids(self, comment_list: list, start_id: int) -> dict:
        """
        fetches mapping of (external_id, article_body_id) to comment_id (given by database) from comment table

        Parameters
        ----------
        comment_list : list
            list of Comment objects
        start_id : int
            database id from which to start the extraction\n
            smallest possible id range for less traffic and response time

        Returns
        -------
        dict
            mapping table for tuple to comment_id as dict\n
             {(external_id, article_body_id) : comment.id}

        """
        article_body_id_list = list(x.get_comment()["data"]["article_body_id"] for x in comment_list)
        article_body_id_tuple = tuple(article_body_id_list)
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_COMMENT_FETCH_ID, (start_id, article_body_id_tuple))
        result = cur.fetchall()  # external_id, article_body_id, id
        if len(result) == 0:
            return {}
        comment_ids = list(((r[0], r[1]), r[2]) for r in result)
        return dict(comment_ids)

    def __fill_comment_ids(self, comment_list: list, start_id: int):
        """
        add database given comment_id to Comment object (after writing to database)

        Parameters
        ----------
        comment_list : list
            list of Comment objects to enrich with body_id\n
            (adding information to input list)
        start_id : int
            database id from which to start the extraction\n
            smallest possible id range for less traffic and response time

        Returns
        -------
        None.

        """
        id_lookup_dict = self.__fetch_comment_ids(comment_list, start_id)
        for comm in comment_list:
            identifier = (comm.get_comment()["data"]["external_id"], comm.get_comment()["data"]["article_body_id"])
            if identifier in id_lookup_dict.keys():
                comm.set_comment_id(id_lookup_dict[identifier])

    def __fetch_old_comment_keys(self, source_id: int, start_date: dt.datetime):
        """
        no functionality right now

        """
        # todo use view to get "not so old" comments from database
        pass

    def __write_comment_data(self, comment_list: list):
        """
         writes comment data for Comment objects in comment_list to comment table

        Parameters
        ----------
        comment_list : list
            list of Comment objects to be written to database

        Returns
        -------
        None.

        """
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SQL_COMMENT_FETCH_START_ID)
        result = cur.fetchall()  # last comment id before current insert run
        if result is None or result[0] is None or result[0][0] is None:
            start_id = 0
        else:
            start_id = result[0]
        for cmt in comment_list:
            if cmt.set_complete():
                data = cmt.get_comment()["data"]
                cur.execute(
                    DatabaseExchange.__SQL_COMMENT_INSERT,
                    (data["article_body_id"], data["external_id"], data["parent_id"], data["level"], data["body"],
                        data["proc_timestamp"])
                )
        self.conn.commit()
        cur.close()
        self.__fill_comment_ids(comment_list, start_id)

    def __write_comment_udfs(self, comment_list: list):
        """
        writes udfs for Comment objects in comment_list to udf_values table

        Parameters
        ----------
        comment_list : list
            list of Comment objects to be written to database

        Returns
        -------
        None.

        """
        cur = self.conn.cursor()
        for cmt in comment_list:
            if not ('id' in cmt.get_comment()["data"].keys()):
                continue
            if cmt.get_comment()["udfs"]:
                for udf in cmt.get_comment()["udfs"]:
                    cur.execute(
                        DatabaseExchange.__SQL_UDF_INSERT,
                        (udf[0], Comment.OBJECT_TYPE, cmt.get_comment()["data"]["id"], udf[1])
                    )
        self.conn.commit()
        cur.close()

    def write_comments(self, comment_list: list) -> bool:
        """
        write full Comment objects from list (data, udfs) to database

        Parameters
        ----------
        comment_list : list
            list of Comment objects to be written to database

        Returns
        -------
        bool
            True if successful

        """
        if type(comment_list) != list:
            return False
        start = 0
        return_value = True  # todo add error handling
        while start < len(comment_list):
            work_list = list(
                filter(lambda x: type(x) == Comment,
                       comment_list[start:start + DatabaseExchange.SUBSET_LENGTH]))

            # todo filter by not in db (use fetchOldCommentKeys)
            comments = work_list
            self.__write_comment_data(comments)
#            print("Comment data written:", start, " - ", start + DatabaseExchange.SUBSET_LENGTH) # todo delete line (debugging purposes only)
            self.__write_comment_udfs(comments)
#            print("Comment udfs written:", start, " - ", start + DatabaseExchange.SUBSET_LENGTH) # todo delete line (debugging purposes only)
            start += DatabaseExchange.SUBSET_LENGTH
        return return_value


def test():
    """
    some test cases
    excluded from ordinary run as it adds garbage to database
    just take a look at the functionality but don't use in production

    Returns
    -------
    None.

    """
    test_article = Article()
    test_article.set_header(
        {"url": "http://www.google.de", "obsolete": False, "source_id": 1, "source_date": dt.date(2020, 12, 1)})
    # test_article.setBody({"proc_timestamp":dt.datetime(2020,12,2,22,0,33),"headline":"example of headline","body":"testText","proc_counter":2,"id":1})
    # test_article.setBodyOld()
    test_article.set_body({"proc_timestamp": dt.datetime.now(pytz.timezone('Europe/Berlin')), "headline": "example of headline", "body": "testText"})
    test_article.add_udf("author", "me")
    test_article.add_udf("label", "smart")
    print("plain Article print")
    test_article.print()
    writer = DatabaseExchange()
    writer.connect()
    print("last Run= ", writer.fetch_scraper_last_run(1))
    writer.log_scraper_start(1)
    writer.write_articles([test_article])
    test_comment = Comment()
    test_comment.set_data(
        {"article_body_id": 141, "level": 0, "body": "i'm a Comment", "proc_timestamp": dt.datetime.now(pytz.timezone('Europe/Berlin'))})
    test_comment.add_udf("author", "brilliant me")
    test_comment.set_external_id((hash("brilliant me" + test_comment.get_comment()["data"]["body"])))
    print("plain Comment print")
    test_comment.print()
    writer.write_comments([test_comment])
    writer.log_scraper_end()
    todo = writer.fetch_scraper_todo_list(1)
    for td in todo:
        td.print()
    writer.close()


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting DatabaseExchange showcase here:\n\n")
    writer = DatabaseExchange()
    # print(writer.fetch_analyzer_todo_list(1))
    # to_do_list=writer.fetch_analyzer_todo_list(1)
    #    writer.write_analyzer_results(1,[{'comment_id':x[0], 'sentiment_value':-1, 'error_value':1} for x in to_do_list])
    print("Topic data fetched: ", len(writer.fetch_topicizer_data()))
    writer.close()
    print("further test deactivated")
