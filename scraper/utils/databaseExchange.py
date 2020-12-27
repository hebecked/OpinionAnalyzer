# -*- coding: utf-8 -*-

# todo: open tasks marked with todo

import datetime as dt

import utils.connectDb as connectDb
from utils.article import Article
from utils.comment import Comment


class DatabaseExchange(connectDb.Database):
    SUBSET_LENGTH = 100  # threshold for database flush
    ANALYZER_RESULT_DEFAULT_COLUMNS = ['id', 'comment_id', 'analyzer_log_id']

    # scraper related database queries
    __SCRAPER_FETCH_LAST_RUN = """SELECT MAX(start_timestamp) 
                                        FROM news_meta_data.crawl_log 
                                        WHERE success = True 
                                            AND source_id = %s;"""

    __SCRAPER_FETCH_TODO = """SELECT article_id, url, article_body_id, headline, body, proc_timestamp, proc_counter 
                                        FROM news_meta_data.v_todo_crawl
                                        WHERE src_id = %s;"""

    # Article related database queries
    __HEADER_MIN_STATEMENT = """SELECT MAX(id) 
                                        FROM news_meta_data.article_header;"""

    __HEADER_STATEMENT = """INSERT INTO news_meta_data.article_header 
                                        (source_date, obsolete, source_id, url) 
                                        VALUES (%s, %s, %s, %s) 
                                        ON CONFLICT DO NOTHING;"""

    __HEADER_ID_FETCH_STATEMENT = """SELECT url, id 
                                        FROM news_meta_data.article_header 
                                        WHERE id > %s 
                                            AND source_id = %s 
                                            AND source_date = %s;"""

    __BODY_MIN_STATEMENT = """SELECT MAX(id) 
                                        FROM news_meta_data.article_body;"""

    __BODY_STATEMENT = """INSERT INTO news_meta_data.article_body 
                                        (article_id, headline, body, proc_timestamp, proc_counter) 
                                        VALUES (%s, %s, %s, %s, %s) 
                                        ON CONFLICT DO NOTHING;"""

    __BODY_UPDATE_STATEMENT = """UPDATE news_meta_data.article_body 
                                        SET proc_counter = %s 
                                        WHERE id = %s;"""

    __BODY_ID_FETCH_STATEMENT = """select article_id, max(id) as id 
                                        FROM  news_meta_data.article_body 
                                        WHERE id > %s 
                                        GROUP BY article_id;"""

    # udf related database queries
    __UDF_INSERT_STATEMENT = """INSERT INTO news_meta_data.udf_values 
                                        (udf_id, object_type, object_id, udf_value) 
                                        VALUES(%s, %s, %s, %s) 
                                        ON CONFLICT DO NOTHING;"""

    # Comment related database queries
    __COMMENT_MIN_STATEMENT = """SELECT MAX(id) 
                                        FROM news_meta_data.Comment;"""

    __COMMENT_STATEMENT = """INSERT INTO news_meta_data.Comment 
                                        (article_body_id, external_id, parent_id, level, body,proc_timestamp) 
                                        VALUES (%s, %s, %s, %s, %s, %s) 
                                        ON CONFLICT DO NOTHING;"""

    __COMMENT_ID_FETCH_STATEMENT = """SELECT external_id, article_body_id, id 
                                        FROM news_meta_data.Comment 
                                        WHERE id > %s 
                                        AND article_body_id IN %s;"""

    # todo get recent comments from view (by source_id and proc_timestamp)

    # logging related database queries
    __LOG_STARTCRAWL = """INSERT INTO news_meta_data.crawl_log 
                                        (source_id, start_timestamp, success) 
                                        VALUES (%s, %s, False);"""

    __LOG_ENDCRAWL = """UPDATE news_meta_data.crawl_log 
                                        SET end_timestamp = %s, 
                                            success = %s 
                                        WHERE id = %s;"""

    #    __LOG_ENDCRAWL_TEST = """SELECT * FROM news_meta_data.crawl_log  WHERE id=%s;"""
    __LOG_GET_MAX_ID = """SELECT MAX(id) 
                                        FROM news_meta_data.crawl_log 
                                        WHERE source_id = %s;"""

    # analyzer related database queries
    __ANALYZER_FETCH_HEADER = """SELECT id, analyzer_view_name, analyzer_table_name 
                                        FROM news_meta_data.analyzer_header;"""

    __ANALYZER_FETCH_TODO = """SELECT comment_id, comment_body 
                                        FROM news_meta_data.{}"""

    __ANALYZER_LOG_START = """INSERT INTO news_meta_data.analyzer_log 
                                        (analyzer_id, comment_id, start_timestamp) 
                                        VALUES (%s, %s, %s);"""

    __ANALYZER_FETCH_LOG_IDs = """SELECT comment_id, max(id) AS id  
                                        FROM news_meta_data.analyzer_log 
                                        WHERE start_timestamp = %s 
                                        AND analyzer_id = %s 
                                        AND comment_id IN %s 
                                        GROUP BY comment_id;"""

    __ANALYZER_GET_TARGET_COLUMNS = """SELECT column_name 
                                        FROM information_schema.columns 
                                        WHERE table_schema = 'news_meta_data' 
                                        AND table_name = %s;"""

    __ANALYZER_LOG_END = """UPDATE news_meta_data.analyzer_log 
                                        SET end_timestamp = %s, 
                                            success=True 
                                        WHERE id = %s 
                                        AND comment_id = %s;"""

    __ANALYZER_INSERT_RESULT = """INSERT INTO news_meta_data.{}
                                        {} 
                                        VALUES %s;"""

    # class variable representing database architecture for analyzers
    __analyzer_data = {}

    # class variables representing current logfile state in db
    __analyzer_ids = {}
    __scraper_log_id = None

    def __init__(self):
        super().__init__()
        print("initializing...")
        self.connect()
        DatabaseExchange.__analyzer_data = self.__fetch_analyzer_tables()
        print("Analyzer tables: ", DatabaseExchange.__analyzer_data)

    def close(self):
        super().close()

    def __del__(self):
        super().__del__()

    def connect(self):
        super().connect()

    def __fetch_analyzer_tables(self):
        # fetch table data for analyzers from header table (which view and target table to use)
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__ANALYZER_FETCH_HEADER)
        result = cur.fetchall()
        cur.close()
        if len(result) == 0:
            return {}
        analyzer_dict = {}
        for res in result:
            analyzer_dict[res[0]] = {'analyzer_view_name': res[1], 'analyzer_table_name': res[2]}
        return analyzer_dict

    def fetch_analyzer_todo_list(self, analyzer_id: int):
        if analyzer_id not in DatabaseExchange.__analyzer_data.keys():
            return []
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__ANALYZER_FETCH_TODO.format(
                DatabaseExchange.__analyzer_data[analyzer_id]['analyzer_view_name']
            )
        )
        result = cur.fetchall()
        cur.close()
        data_set = set([])
        for res in result:
            data_set |= {res}
        todo_list = list(data_set)
        self.__log_analyzer_start(analyzer_id, todo_list)
        return todo_list

    def __log_analyzer_start(self, analyzer_id: int, analyzer_todo_list: list):
        if analyzer_id not in DatabaseExchange.__analyzer_data.keys():
            return False
        self.__analyzer_start_timestamp = dt.datetime.today()
        cur = self.conn.cursor()
        for cmt in analyzer_todo_list:
            cur.execute(
                DatabaseExchange.__ANALYZER_LOG_START,
                (analyzer_id, cmt[0], self.__analyzer_start_timestamp)
            )
        DatabaseExchange.__analyzer_ids.update(
            self.__fetch_analyzer_log_ids(analyzer_id, list(c[0] for c in analyzer_todo_list))
        )
        self.conn.commit()
        cur.close()

    def __fetch_analyzer_log_ids(self, analyzer_id: int, comment_ids: list):
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__ANALYZER_FETCH_LOG_IDs,
            (self.__analyzer_start_timestamp, analyzer_id, tuple(comment_ids))
        )
        ids = cur.fetchall()
        cur.close()
        if len(ids) == 0:
            return {}
        return dict(ids)

    def __fetch_analyzer_columns(self, analyzer_id: int):
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__ANALYZER_GET_TARGET_COLUMNS,
            (DatabaseExchange.__analyzer_data[analyzer_id]['analyzer_table_name'],)
        )
        table_fields = cur.fetchall()
        if len(table_fields) == 0:
            cur.close()
            return set([])
        columns = set(f[0] for f in table_fields) - set(DatabaseExchange.ANALYZER_RESULT_DEFAULT_COLUMNS)
        cur.close()
        return list(columns)

    def write_analyzer_results(self, analyzer_id: int, analyzer_result: list):
        if not type(analyzer_result) == list:
            return False
        if analyzer_id not in DatabaseExchange.__analyzer_data.keys():
            return False
        analyzer_end_timestamp = dt.datetime.today()
        target_columns = self.__fetch_analyzer_columns(analyzer_id)
        cols = tuple(DatabaseExchange.ANALYZER_RESULT_DEFAULT_COLUMNS[1:] + target_columns)
        columns_as_string = '(' + ','.join(cols) + ')'
        cur = self.conn.cursor()
        for result in analyzer_result:
            if not type(result) == dict:
                continue
            insert_sql = DatabaseExchange.__ANALYZER_INSERT_RESULT.format(
                DatabaseExchange.__analyzer_data[analyzer_id]['analyzer_table_name'],
                columns_as_string
            )
            values = (result['comment_id'], DatabaseExchange.__analyzer_ids[result['comment_id']])
            if not (set(target_columns) - set(result.keys())):  # if missing columns is empty
                for col in target_columns:
                    values += tuple([result[col]])
                insert_sql.format(values)
                cur.execute(insert_sql, (values,))
                cur.execute(
                    DatabaseExchange.__ANALYZER_LOG_END,
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

    def fetch_scraper_todo_list(self, source_id: int):
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SCRAPER_FETCH_TODO,
            (source_id,)
        )
        result = cur.fetchall()
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

    def fetch_scraper_last_run(self, source_id: int):
        cur = self.conn.cursor()
        cur.execute(
            DatabaseExchange.__SCRAPER_FETCH_LAST_RUN,
            (source_id,)
        )
        result = cur.fetchall()
        cur.close()
        if result[0][0] is None:
            return dt.datetime(1990, 1, 1)
        return result[0][0]

    def log_scraper_start(self, source_id: int):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__LOG_STARTCRAWL,
                    (source_id, dt.datetime.today().replace(microsecond=0).isoformat()))
        self.conn.commit()
        cur.execute(DatabaseExchange.__LOG_GET_MAX_ID, (source_id,))
        result = cur.fetchall()
        cur.close()
        if result[0][0] is None:
            return False
        DatabaseExchange.__scraper_log_id = result[0][0]
        print("logId: ", DatabaseExchange.__scraper_log_id)
        return True

    def log_scraper_end(self, success: bool = True):
        cur = self.conn.cursor()
        argument_tuple = (
            dt.datetime.today().replace(microsecond=0).isoformat(), success, DatabaseExchange.__scraper_log_id
        )
        cur.execute(
            DatabaseExchange.__LOG_ENDCRAWL,
            argument_tuple
        )
        self.conn.commit()
        cur.close()

    def __fetch_article_ids(self, articles_list: list, start_id: int):
        article_ids = []
        cur = self.conn.cursor()
        for source_dates in set(
                (x.get_article()["header"]["source_id"], x.get_article()["header"]["source_date"])
                for x in articles_list):
            cur.execute(
                DatabaseExchange.__HEADER_ID_FETCH_STATEMENT,
                tuple([start_id] + list(source_dates))
            )
            result = cur.fetchall()
            article_ids += list(result)
        cur.close()
        return dict(article_ids)

    def __fetch_body_ids(self, start_id: int):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__BODY_ID_FETCH_STATEMENT, (start_id,))
        result = cur.fetchall()
        if len(result) == 0:
            return {}
        body_ids = list(result)
        return dict(body_ids)

    def __write_article_headers(self, article_list: list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__HEADER_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0] is None:
            start_id = 0
        else:
            start_id = result[0][0]  # todo check if correct
        for art in article_list:
            if art.set_header_complete():
                hdr = art.get_article()["header"]
                cur.execute(
                    DatabaseExchange.__HEADER_STATEMENT,
                    (hdr["source_date"], hdr["obsolete"], hdr["source_id"], hdr["url"])
                )
        self.conn.commit()
        cur.close()
        self.__fill_header_ids(article_list, start_id)

    def __write_article_bodies(self, article_list: list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__BODY_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0] is None:
            start_id = 0
        else:
            start_id = result[0][0]  # todo check if correct
        for art in article_list:
            if art.set_body_complete():
                body_to_use = art.get_body_to_write()
                if body_to_use["insert"]:
                    cur.execute(DatabaseExchange.__BODY_STATEMENT, (
                        body_to_use["body"]["article_id"], body_to_use["body"]["headline"], body_to_use["body"]["body"],
                        body_to_use["body"]["proc_timestamp"], body_to_use["body"]["proc_counter"] + 1))
                else:
                    cur.execute(DatabaseExchange.__BODY_UPDATE_STATEMENT,
                                (body_to_use["body"]["proc_counter"] + 1, body_to_use["body"]["id"]))
        self.conn.commit()
        cur.close()
        self.__fill_body_ids(article_list, start_id)

    def __write_article_udfs(self, article_list: list):
        cur = self.conn.cursor()
        for art in article_list:
            if art.get_body_to_write()["insert"]:
                for udf in art.get_article()["udfs"]:
                    cur.execute(
                        DatabaseExchange.__UDF_INSERT_STATEMENT,
                        (udf[0], Article.OBJECT_TYPE, art.get_article()["body"]["id"], udf[1])
                    )
        self.conn.commit()
        cur.close()

    def __fill_header_ids(self, article_list: list, start_id: int):
        id_lookup_dict = self.__fetch_article_ids(article_list, start_id)
        for art in article_list:
            url = art.get_article()["header"]["url"]
            if url in id_lookup_dict.keys():
                art.set_header_id(id_lookup_dict[url])

    def __fill_body_ids(self, article_list: list, start_id: int):
        id_lookup_dict = self.__fetch_body_ids(start_id)
        for art in article_list:
            article_id = art.get_article()["header"]["id"]
            if article_id in id_lookup_dict.keys():
                art.set_body_id(id_lookup_dict[article_id])

    def write_articles(self, article_list: list):
        if type(article_list) != list:
            return False
        start = 0
        while start < len(article_list):
            work_list = list(
                filter(lambda x: type(x) == Article,
                       article_list[start:start + DatabaseExchange.SUBSET_LENGTH]))
            headers = list(filter(lambda x: not (x.is_in_db()), work_list))
            self.__write_article_headers(headers)
            print("Article headers written and id added")
            bodies = list(filter(lambda x: x.is_in_db(), work_list))
            self.__write_article_bodies(bodies)
            print("Article bodies written and id added")
            self.__write_article_udfs(bodies)
            print("Article udfs written")
            start += DatabaseExchange.SUBSET_LENGTH

    def __fetch_comment_ids(self, comment_list: list, start_id: int):
        article_body_id_list = list(x.get_comment()["data"]["article_body_id"] for x in comment_list)
        article_body_id_tuple = tuple(article_body_id_list)
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__COMMENT_ID_FETCH_STATEMENT, (start_id, article_body_id_tuple))
        result = cur.fetchall()
        if len(result) == 0:
            return {}
        comment_ids = list(((r[0], r[1]), r[2]) for r in result)
        return dict(comment_ids)

    def __fill_comment_ids(self, comment_list: list, start_id: int):
        id_lookup_dict = self.__fetch_comment_ids(comment_list, start_id)
        for comm in comment_list:
            identifier = (comm.get_comment()["data"]["external_id"], comm.get_comment()["data"]["article_body_id"])
            if identifier in id_lookup_dict.keys():
                comm.set_comment_id(id_lookup_dict[identifier])

    def __fetch_old_comment_keys(self, source_id: int, start_date: dt.datetime):
        # todo use view to get "not so old" comments from database
        pass

    def __write_comment_data(self, comment_list: list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__COMMENT_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0] is None:
            start_id = 0
        else:
            start_id = result[0]
        for cmt in comment_list:
            if cmt.set_complete():
                data = cmt.get_comment()["data"]
                cur.execute(
                    DatabaseExchange.__COMMENT_STATEMENT,
                    (data["article_body_id"], data["external_id"], data["parent_id"], data["level"], data["body"],
                        data["proc_timestamp"])
                )
        self.conn.commit()
        cur.close()
        self.__fill_comment_ids(comment_list, start_id)

    def __write_comment_udfs(self, comment_list: list):
        cur = self.conn.cursor()
        for cmt in comment_list:
            if not ('id' in cmt.get_comment()["data"].keys()):
                continue
            if cmt.get_comment()["udfs"]:
                for udf in cmt.get_comment()["udfs"]:
                    cur.execute(
                        DatabaseExchange.__UDF_INSERT_STATEMENT,
                        (udf[0], Comment.OBJECT_TYPE, cmt.get_comment()["data"]["id"], udf[1])
                    )
        self.conn.commit()
        cur.close()

    def write_comments(self, comment_list: list):
        if type(comment_list) != list:
            return False
        start = 0
        while start < len(comment_list):
            work_list = list(
                filter(lambda x: type(x) == Comment,
                       comment_list[start:start + DatabaseExchange.SUBSET_LENGTH]))

            # todo filter by not in db (use fetchOldCommentKeys)
            comments = work_list
            self.__write_comment_data(comments)
            print("Comment data written:", start, " - ", start + DatabaseExchange.SUBSET_LENGTH)
            self.__write_comment_udfs(comments)
            print("Comment udfs written:", start, " - ", start + DatabaseExchange.SUBSET_LENGTH)
            start += DatabaseExchange.SUBSET_LENGTH


def test():
    test_article = Article()
    test_article.set_header(
        {"url": "http://www.google.de", "obsolete": False, "source_id": 1, "source_date": dt.date(2020, 12, 1)})
    # test_article.setBody({"proc_timestamp":dt.datetime(2020,12,2,22,0,33),"headline":"example of headline","body":"testText","proc_counter":2,"id":1})
    # test_article.setBodyOld()
    test_article.set_body({"proc_timestamp": dt.datetime.today(), "headline": "example of headline", "body": "testText"})
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
        {"article_body_id": 141, "level": 0, "body": "i'm a Comment", "proc_timestamp": dt.datetime.today()})
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
    print("Starting DatabaseExchange testcases here:\n\n")
    writer = DatabaseExchange()
    # print(writer.fetchTodoListAnalyzer(1))
    #    todo=writer.fetchTodoListAnalyzer(1)
    #    writer.writeAnalyzerResults(1,[{'comment_id':x[0], 'sentiment_value':-1, 'error_value':1} for x in todo])
    writer.close()
    print("further test deactivated")
