# -*- coding: utf-8 -*-

#todo: open tasks marked with todo

import utils.connectDb as connectDb
from utils.article import Article
from utils.comment import Comment
import datetime as dt

#add comments, rename to dataExchange
#add getUdfs(), getSources() for Article and Comment object

class DatabaseExchange(connectDb.database):
    SUBSET_LENGTH=100   #threshold for database flush
    ANALYZER_RESULT_DEFAULT_COLUMNS=['id','comment_id','analyzer_log_id']
    #scraper related database queries
    __SCRAPER_FETCH_LAST_RUN="""SELECT MAX(start_timestamp) FROM news_meta_data.crawl_log WHERE success=True and source_id=%s;"""    
    __SCRAPER_FETCH_TODO="""SELECT article_id,url,article_body_id,headline,body,proc_timestamp,proc_counter FROM news_meta_data.v_todo_crawl WHERE src_id=%s;"""

    #Article related database queries
    __HEADER_MIN_STATEMENT="""SELECT MAX(id) FROM news_meta_data.article_header;"""
    __HEADER_STATEMENT="""INSERT INTO news_meta_data.article_header (source_date,obsolete,source_id,url) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __HEADER_ID_FETCH_STATEMENT="""SELECT url, id FROM news_meta_data.article_header WHERE id > %s AND source_id=%s AND source_date=%s;"""

    __BODY_MIN_STATEMENT="""SELECT MAX(id) from news_meta_data.article_body;"""
    __BODY_STATEMENT="""INSERT INTO news_meta_data.article_body (article_id, headline, body, proc_timestamp, proc_counter) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __BODY_UPDATE_STATEMENT="""UPDATE news_meta_data.article_body set proc_counter=%s where id=%s;"""
    __BODY_ID_FETCH_STATEMENT="""select article_id, max(id) as id FROM  news_meta_data.article_body where id > %s group by article_id;"""

    #udf related database queries
    __UDF_INSERT_STATEMENT="""INSERT INTO news_meta_data.udf_values (udf_id,object_type,object_id,udf_value) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""

    #Comment related database queries
    __COMMENT_MIN_STATEMENT="""SELECT MAX(id) FROM news_meta_data.Comment;"""
    __COMMENT_STATEMENT="""INSERT INTO news_meta_data.Comment (article_body_id, external_id, parent_id, level, body,proc_timestamp ) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __COMMENT_ID_FETCH_STATEMENT="""SELECT external_id, article_body_id, id FROM news_meta_data.Comment WHERE id > %s AND article_body_id in %s;"""
#todo get recent comments from view (by source_id and proc_timestamp)
    
    #logging related database queries
    __LOG_STARTCRAWL="""INSERT INTO news_meta_data.crawl_log (source_id,start_timestamp, success) VALUES (%s, %s,False);"""
    __LOG_ENDCRAWL="""UPDATE news_meta_data.crawl_log SET end_timestamp=%s, success=%s WHERE id=%s;"""
    __LOG_ENDCRAWL_TEST="""SELECT * FROM news_meta_data.crawl_log  WHERE id=%s;"""
    __LOG_GET_MAX_ID="""SELECT MAX(id) FROM news_meta_data.crawl_log WHERE source_id=%s;"""
    
    #analyzer related database queries
    __ANALYZER_FETCH_HEADER="""SELECT id, analyzer_view_name, analyzer_table_name FROM news_meta_data.analyzer_header;"""
    __ANALYZER_FETCH_TODO="""SELECT comment_id, comment_body FROM news_meta_data.{}"""
    __ANALYZER_LOG_START="""INSERT INTO news_meta_data.analyzer_log (analyzer_id,comment_id, start_timestamp) VALUES (%s,%s,%s);"""
    __ANALYZER_FETCH_LOG_IDs="""SELECT comment_id, max(id) AS id  FROM  news_meta_data.analyzer_log where start_timestamp=%s and analyzer_id=%s and comment_id in %s GROUP BY comment_id;"""
    __ANALYZER_GET_TARGET_COLUMNS="""SELECT column_name FROM information_schema.columns WHERE table_schema='news_meta_data' AND table_name=%s;"""
    __ANALYZER_LOG_END="""UPDATE news_meta_data.analyzer_log SET end_timestamp=%s, success=True WHERE id=%s AND comment_id =%s;"""
    __ANALYZER_INSERT_RESULT="""INSERT INTO news_meta_data.{} {} VALUES %s;"""
    
    #class variable representing database architecture for analyzers
    __analyzer_data={}
    
    #class variables representing current logfile state in db
    __analyzerIds={}
    __scraperLogId=None
        

    def __init__(self):
        super().__init__()
        print("initializing...")
        self.connect()
        DatabaseExchange.__analyzer_data=self.__fetchAnalyzerTables()
        print("Analyzer tables: ", DatabaseExchange.__analyzer_data)
        
    def close(self):
        super().close()
        
    def __del__(self):
        super().__del__()
        
    def connect(self):
        super().connect()
        
    def __fetchAnalyzerTables(self):
        #fetch table data for analyzers from header table (which view and target table to use)
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__ANALYZER_FETCH_HEADER)
        result = cur.fetchall()
        cur.close()
        if len(result)==0: return {}
        analyzerDict={}
        for res in result:
            analyzerDict[res[0]]={'analyzer_view_name':res[1],'analyzer_table_name':res[2]}
        return analyzerDict

        
    def fetchTodoListAnalyzer(self, analyzerId:int):
        if not analyzerId in DatabaseExchange.__analyzer_data.keys(): return []
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__ANALYZER_FETCH_TODO.format(DatabaseExchange.__analyzer_data[analyzerId]['analyzer_view_name']))
        result = cur.fetchall()
        cur.close()
        dataSet=set([])
        for res in result:
            dataSet|=set([res])
        returnList=list(dataSet)
        self.__logStartAnalyzer(analyzerId,returnList)
        return returnList
    
    def __logStartAnalyzer(self, analyzerId:int, analyzerTodoList: list):
        if not analyzerId in DatabaseExchange.__analyzer_data.keys(): return False
        self.__analyzerStart=dt.datetime.today()
        cur = self.conn.cursor()
        [cur.execute(DatabaseExchange.__ANALYZER_LOG_START, (analyzerId, x[0], self.__analyzerStart)) for x in analyzerTodoList]
        DatabaseExchange.__analyzerIds.update(self.__fetchAnalyzerLogIds(analyzerId, list(c[0] for c in analyzerTodoList)))
        self.conn.commit()
        cur.close()

    def __fetchAnalyzerLogIds(self, analyzerId:int, commentIds: list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__ANALYZER_FETCH_LOG_IDs, (self.__analyzerStart, analyzerId, tuple(commentIds)))
        ids = cur.fetchall()
        cur.close()   
        if len(ids)==0: 
            return {}
        return dict(ids)
    
    def __fetchAnalyzerColums(self, analyzerId:int):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__ANALYZER_GET_TARGET_COLUMNS, (DatabaseExchange.__analyzer_data[analyzerId]['analyzer_table_name'],))
        table_fields = cur.fetchall()
        if len(table_fields)==0:
            cur.close()   
            return set([])
        columns = set(f[0] for f in table_fields)-set(DatabaseExchange.ANALYZER_RESULT_DEFAULT_COLUMNS)
        cur.close()
        return list(columns)
    
    def writeAnalyzerResults(self, analyzerId:int, analyzerResult: list):
        if not type(analyzerResult)==list: return False
        if not analyzerId in DatabaseExchange.__analyzer_data.keys(): return False
        analyzerEnd=dt.datetime.today()
        targetColumns=self.__fetchAnalyzerColums(analyzerId)
        cols=tuple(DatabaseExchange.ANALYZER_RESULT_DEFAULT_COLUMNS[1:] + targetColumns)
        colString='('+','.join(cols)+')'
        cur = self.conn.cursor()
        for result in analyzerResult:
            if not type(result)==dict:continue
            insert=DatabaseExchange.__ANALYZER_INSERT_RESULT.format(DatabaseExchange.__analyzer_data[analyzerId]['analyzer_table_name'], colString)
            values=(result['comment_id'], DatabaseExchange.__analyzerIds[result['comment_id']])
            if not(set(targetColumns) - set(result.keys())):
                for col in targetColumns:
                    values+=tuple([result[col]])
                insert.format(values)
                cur.execute(insert,(values,))
                cur.execute(DatabaseExchange.__ANALYZER_LOG_END, (analyzerEnd, DatabaseExchange.__analyzerIds[result['comment_id']], result['comment_id']))
        self.conn.commit()
        cur.close()
        keys=DatabaseExchange.__analyzerIds.keys()
        for result in analyzerResult:
            if result['comment_id']in keys:
                del DatabaseExchange.__analyzerIds[result['comment_id']]
        return True

             
    def fetchTodoListScraper(self, sourceId:int):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SCRAPER_FETCH_TODO, (sourceId,))
        result = cur.fetchall()
        cur.close()
        if len(result)==0: return []
        returnList=[]
        for res in result:
            art=Article()
            art.setHeader({'id':res[0],'url':res[1],'source_id':sourceId})
            if(res[2]!=None):
                art.setBody({'id':res[2],'article_id':res[0],'headline':res[3],'body':res[4],'proc_timestamp':res[5],'proc_counter':res[6]})
                art.setBodyOld()
            returnList+=[art]
        return returnList
    def fetchLastRun(self,sourceId:int):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__SCRAPER_FETCH_LAST_RUN, (sourceId,))
        result = cur.fetchall()
        cur.close()
        if result[0][0]==None: return dt.datetime(1990,1,1)
        return result[0][0]
    
    def logStartCrawl(self,sourceId:int):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__LOG_STARTCRAWL, (sourceId, dt.datetime.today().replace(microsecond=0).isoformat()))
        self.conn.commit()
        cur.execute(DatabaseExchange.__LOG_GET_MAX_ID, (sourceId,))
        result = cur.fetchall()
        cur.close()
        if result[0][0]==None: return False
        DatabaseExchange.__scraperLogId=result[0][0]
        print("logId: ", DatabaseExchange.__scraperLogId)
        return True

    def logEndCrawl(self,success:bool=True):
        cur = self.conn.cursor()
        argument_tuple=(dt.datetime.today().replace(microsecond=0).isoformat(), success, DatabaseExchange.__scraperLogId)
        cur.execute(DatabaseExchange.__LOG_ENDCRAWL, argument_tuple)
        self.conn.commit()        
        cur.close()
        

    def fetchArticleIds(self, articlesList:list, startId:int):
        articleIds=[]
        cur = self.conn.cursor()
        for sourcesDates in set((x.getArticle()["header"]["source_id"],x.getArticle()["header"]["source_date"]) for x in articlesList):
            cur.execute(DatabaseExchange.__HEADER_ID_FETCH_STATEMENT, tuple([startId] + list(sourcesDates)))
            result = cur.fetchall()
            articleIds+=list(result)
        cur.close()
        return dict(articleIds)
    
    def fetchBodyIds(self, articlesList:list, startId:int):
        bodyIds=[]       
        cur = self.conn.cursor()        
        cur.execute(DatabaseExchange.__BODY_ID_FETCH_STATEMENT, (startId,))
        result = cur.fetchall()
        if len(result)==0: return {}
        bodyIds=list(result)       
        return dict(bodyIds)
    
    def __writeHeaders(self, articlesList:list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__HEADER_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0][0]  #todo check if correct
        for art in articlesList:
            if (art.setHeaderComplete()):
                hdr=art.getArticle()["header"]
                cur.execute(DatabaseExchange.__HEADER_STATEMENT, (hdr["source_date"], hdr["obsolete"], hdr["source_id"], hdr["url"]))
        self.conn.commit()
        cur.close()
        self.fillHeaderIds(articlesList,startId)

    
    def __writeBodies(self, articlesList:list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__BODY_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0][0]  #todo check if correct
        for art in articlesList:
            if (art.setBodyComplete()):
                todo=art.getBodyToWrite()
                if(todo["insert"]):
                    cur.execute(DatabaseExchange.__BODY_STATEMENT, (todo["body"]["article_id"], todo["body"]["headline"], todo["body"]["body"], todo["body"]["proc_timestamp"], todo["body"]["proc_counter"] + 1))
                else:
                    cur.execute(DatabaseExchange.__BODY_UPDATE_STATEMENT, (todo["body"]["proc_counter"] + 1, todo["body"]["id"]))
        self.conn.commit()
        cur.close()
        self.fillBodyIds(articlesList,startId)
    
    def __writeArticleUdfs(self, articlesList:list):
        cur = self.conn.cursor()
        for art in articlesList:
            if art.getBodyToWrite()["insert"]:
                for udf in art.getArticle()["udfs"]:
                    cur.execute(DatabaseExchange.__UDF_INSERT_STATEMENT, (udf[0], Article.OBJECT_TYPE, art.getArticle()["body"]["id"], udf[1]))
        self.conn.commit()
        cur.close()            
    
    def fillHeaderIds(self,articlesList:list, startId: int):
        Ids=self.fetchArticleIds(articlesList,startId)
        for art in articlesList:
            url=art.getArticle()["header"]["url"]
            if url in Ids.keys():
                art.setHeaderId(Ids[url])
                
    def fillBodyIds(self,articlesList:list, startId: int):
        Ids=self.fetchBodyIds(articlesList,startId)
        for art in articlesList:
            articleId=art.getArticle()["header"]["id"]
            if articleId in Ids.keys():
                art.setBodyId(Ids[articleId])    
        
    
    def writeArticles(self, articlesList:list):
        if(type(articlesList)!=list): return False
        start=0
        while start < len(articlesList):
            worklist=list(filter(lambda x: type(x) == Article, articlesList[start:start + DatabaseExchange.SUBSET_LENGTH]))
            headers=list(filter(lambda x: not(x.isInDb()),worklist))
            self.__writeHeaders(headers)
            #headers[0].print()
            print("Article headers written and id added")
            #worklist[0].print()
            bodies=list(filter(lambda x: x.isInDb(),worklist))
            self.__writeBodies(bodies)
            print("Article bodies written and id added")
            #bodies[0].print()
            self.__writeArticleUdfs(bodies)   
            print("Article udfs written")
            start+=DatabaseExchange.SUBSET_LENGTH

    def fetchCommentIds(self, commentsList:list, startId:int):
        article_body_id_List=list(x.getComment()["data"]["article_body_id"] for x in commentsList)
        article_body_id_tuple=tuple(article_body_id_List)
        commentIds=[]       
        cur = self.conn.cursor()        
        cur.execute(DatabaseExchange.__COMMENT_ID_FETCH_STATEMENT, (startId, article_body_id_tuple))
        result = cur.fetchall()
        if len(result)==0: return {}
        commentIds=list(((r[0],r[1]),r[2]) for r in result)       
        return dict(commentIds)        

    def fillCommentIds(self, commentsList:list, startId:int):
        Ids=self.fetchCommentIds(commentsList,startId)
        for comm in commentsList:
            identifier=(comm.getComment()["data"]["external_id"],comm.getComment()["data"]["article_body_id"])
            if identifier in Ids.keys():
                comm.setCommentId(Ids[identifier])    
    
    def fetchOldCommentKeys(self, sourceId: int, startdate:dt.datetime):
# todo use view to get "not so old" comments from database
        
        pass
    def __writeCommentData(self, commentsList:list):
        cur = self.conn.cursor()
        cur.execute(DatabaseExchange.__COMMENT_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0]
        for comm in commentsList:
            if (comm.setComplete()):
                data=comm.getComment()["data"]
                cur.execute(DatabaseExchange.__COMMENT_STATEMENT, (data["article_body_id"], data["external_id"], data["parent_id"], data["level"], data["body"], data["proc_timestamp"]))
        self.conn.commit()
        cur.close()
        self.fillCommentIds(commentsList,startId)
        
    def __writeCommentUdfs(self, commentsList:list):
        cur = self.conn.cursor()
        for comm in commentsList:
            if not('id' in comm.getComment()["data"].keys()):
                continue
            if comm.getComment()["udfs"]:
                for udf in comm.getComment()["udfs"]:
                    cur.execute(DatabaseExchange.__UDF_INSERT_STATEMENT, (udf[0], Comment.OBJECT_TYPE, comm.getComment()["data"]["id"], udf[1]))
        self.conn.commit()
        cur.close()   
    
    def writeComments(self, commentsList:list):
        if(type(commentsList)!=list): return False
        start=0
        while start < len(commentsList):
            worklist=list(filter(lambda x: type(x) == Comment, commentsList[start:start + DatabaseExchange.SUBSET_LENGTH]))
            
            # todo filter by not in db (use fetchOldCommentKeys)
            comments=worklist
            
            self.__writeCommentData(comments)
            print("Comment data written:", start," - ", start + DatabaseExchange.SUBSET_LENGTH)
            self.__writeCommentUdfs(comments)
            print("Comment udfs written:", start," - ", start + DatabaseExchange.SUBSET_LENGTH)
            start+=DatabaseExchange.SUBSET_LENGTH
    
def test():
    testArticle=Article()
    testArticle.setHeader({"url":"http://www.google.de","obsolete":False,"source_id":1,"source_date":dt.date(2020,12,1)})
    #testArticle.setBody({"proc_timestamp":dt.datetime(2020,12,2,22,0,33),"headline":"example of headline","body":"testText","proc_counter":2,"id":1})
    #testArticle.setBodyOld()
    testArticle.setBody({"proc_timestamp":dt.datetime.today(),"headline":"example of headline","body":"testText"})
    testArticle.addUdf("author","me")
    testArticle.addUdf("label","smart")
    print("plain Article print")
    testArticle.print()
    writer=DatabaseExchange()
    writer.connect()
    print("last Run= ",writer.fetchLastRun(1))
    writer.logStartCrawl(1)
    writer.writeArticles([testArticle])
    testComment=Comment()
    testComment.setData({"article_body_id":141,"level":0,"body":"i'm a Comment","proc_timestamp":dt.datetime.today()})
    testComment.addUdf("author","brilliant me")
    testComment.setExternalId((hash("brilliant me"+testComment.getComment()["data"]["body"])))
    print("plain Comment print")
    testComment.print()
    writer.writeComments([testComment])
    writer.logEndCrawl()
    todo=writer.fetchTodoListScraper(1)
    for td in todo:
        td.print()
    writer.close()


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting DatabaseExchange testcases here:\n\n")
    writer=DatabaseExchange()
    #print(writer.fetchTodoListAnalyzer(1))
#    todo=writer.fetchTodoListAnalyzer(1)
#    writer.writeAnalyzerResults(1,[{'comment_id':x[0], 'sentiment_value':-1, 'error_value':1} for x in todo])
    writer.close()
    print("further test deactivated")

