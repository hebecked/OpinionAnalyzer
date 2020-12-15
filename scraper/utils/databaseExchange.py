# -*- coding: utf-8 -*-

#todo: open tasks marked with todo

import utils.connectDb as connectDb
from utils.article import article
from utils.comment import comment
import datetime as dt

#add comments, rename to dataExchange
#add getUdfs(), getSources() for article and comment object

class databaseExchange(connectDb.database):
    SUBSET_LENGTH=100   #threshold for database flush
    #scraper related database queries
    __SCRAPER_FETCH_LAST_RUN="""SELECT MAX(start_timestamp) FROM news_meta_data.crawl_log WHERE success=True and source_id=%s;"""    
#todo change WHERE clause: sourceId instead of source
    __SCRAPER_FETCH_TODO="""SELECT article_id,url,article_body_id,headline,body,proc_timestamp,proc_counter FROM news_meta_data.v_todo_crawl WHERE src_id=%s;"""

    #article related database queries
    __HEADER_MIN_STATEMENT="""SELECT MAX(id) FROM news_meta_data.article_header;"""
    __HEADER_STATEMENT="""INSERT INTO news_meta_data.article_header (source_date,obsolete,source_id,url) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __HEADER_ID_FETCH_STATEMENT="""SELECT url, id FROM news_meta_data.article_header WHERE id > %s AND source_id=%s AND source_date=%s;"""

    __BODY_MIN_STATEMENT="""SELECT MAX(id) from news_meta_data.article_body;"""
    __BODY_STATEMENT="""INSERT INTO news_meta_data.article_body (article_id, headline, body, proc_timestamp, proc_counter) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __BODY_UPDATE_STATEMENT="""UPDATE news_meta_data.article_body set proc_counter=%s where id=%s;"""
    __BODY_ID_FETCH_STATEMENT="""select article_id, max(id) as id from  news_meta_data.article_body where id > %s group by article_id;"""

    #udf related database queries
    __UDF_INSERT_STATEMENT="""INSERT INTO news_meta_data.udf_values (udf_id,object_type,object_id,udf_value) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""

    #comment related database queries
    __COMMENT_MIN_STATEMENT="""SELECT MAX(id) FROM news_meta_data.comment;"""
    __COMMENT_STATEMENT="""INSERT INTO news_meta_data.comment (article_body_id, external_id, parent_id, level, body,proc_timestamp ) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __COMMENT_ID_FETCH_STATEMENT="""SELECT external_id, article_body_id, id FROM news_meta_data.comment WHERE id > %s AND article_body_id in %s;"""    
#todo get recent comments from view (by source_id and proc_timestamp)
    
    #logging related database queries
    __LOG_STARTCRAWL="""INSERT INTO news_meta_data.crawl_log (source_id,start_timestamp, success) VALUES (%s, %s,False);"""
    __LOG_ENDCRAWL="""UPDATE news_meta_data.crawl_log SET end_timestamp=%s, success=%s WHERE id=%s;"""
    __LOG_ENDCRAWL_TEST="""SELECT * FROM news_meta_data.crawl_log  WHERE id=%s;"""
    __LOG_GET_MAX_ID="""SELECT MAX(id) FROM news_meta_data.crawl_log WHERE source_id=%s;"""
    

    def __init__(self):
        super().__init__()
        self.__logId=None
        
    def close(self):
        super().close()
        
    def __del__(self):
        super().__del__()
        
    def connect(self):
        super().connect()
              
    def fetchTodoList(self, sourceId:int):
        cur = self.conn.cursor()
        cur.execute(databaseExchange.__SCRAPER_FETCH_TODO,(sourceId,))
        result = cur.fetchall()
        cur.close()
        if len(result)==0: return []
        returnList=[]
        for res in result:
            art=article()
            art.setHeader({'id':res[0],'url':res[1],'source_id':sourceId})
            if(res[2]!=None):
                art.setBody({'id':res[2],'article_id':res[0],'headline':res[3],'body':res[4],'proc_timestamp':res[5],'proc_counter':res[6]})
                art.setBodyOld()
            returnList+=[art]
        return returnList
    def fetchLastRun(self,sourceId:int):
        cur = self.conn.cursor()
        cur.execute(databaseExchange.__SCRAPER_FETCH_LAST_RUN,(sourceId,))
        result = cur.fetchall()
        cur.close()
        if result[0][0]==None: return dt.datetime(1990,1,1)
        return result[0][0]
    
    def logStartCrawl(self,sourceId:int):
        cur = self.conn.cursor()
        cur.execute(databaseExchange.__LOG_STARTCRAWL,(sourceId,dt.datetime.today().replace(microsecond=0).isoformat()))
        self.conn.commit()
        cur.execute(databaseExchange.__LOG_GET_MAX_ID,(sourceId,))
        result = cur.fetchall()
        cur.close()
        if result[0][0]==None: return False
        self.__logId=result[0][0]
        print("logId: ",self.__logId)
        return True

    def logEndCrawl(self,success:bool=True):
        cur = self.conn.cursor()
        argument_tuple=(dt.datetime.today().replace(microsecond=0).isoformat(),success,self.__logId)
        cur.execute(databaseExchange.__LOG_ENDCRAWL,argument_tuple)
        self.conn.commit()        
        cur.close()
        

    def fetchArticleIds(self, articlesList:list, startId:int):
        articleIds=[]
        cur = self.conn.cursor()
        for sourcesDates in set((x.getArticle()["header"]["source_id"],x.getArticle()["header"]["source_date"]) for x in articlesList):
            cur.execute(databaseExchange.__HEADER_ID_FETCH_STATEMENT,tuple([startId]+list(sourcesDates)))
            result = cur.fetchall()
            articleIds+=list(result)
        cur.close()
        return dict(articleIds)
    
    def fetchBodyIds(self, articlesList:list, startId:int):
        bodyIds=[]       
        cur = self.conn.cursor()        
        cur.execute(databaseExchange.__BODY_ID_FETCH_STATEMENT,(startId,))
        result = cur.fetchall()
        if len(result)==0: return {}
        bodyIds=list(result)       
        return dict(bodyIds)
    
    def __writeHeaders(self, articlesList:list):
        cur = self.conn.cursor()
        cur.execute(databaseExchange.__HEADER_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0][0]  #todo check if correct
        for art in articlesList:
            if (art.setHeaderComplete()):
                hdr=art.getArticle()["header"]
                cur.execute(databaseExchange.__HEADER_STATEMENT,(hdr["source_date"],hdr["obsolete"],hdr["source_id"],hdr["url"]))
        self.conn.commit()
        cur.close()
        self.fillHeaderIds(articlesList,startId)

    
    def __writeBodies(self, articlesList:list):
        cur = self.conn.cursor()
        cur.execute(databaseExchange.__BODY_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0][0]  #todo check if correct
        for art in articlesList:
            if (art.setBodyComplete()):
                todo=art.getBodyToWrite()
                if(todo["insert"]):
                    cur.execute(databaseExchange.__BODY_STATEMENT,(todo["body"]["article_id"],todo["body"]["headline"],todo["body"]["body"],todo["body"]["proc_timestamp"],todo["body"]["proc_counter"]+1))
                else:
                    cur.execute(databaseExchange.__BODY_UPDATE_STATEMENT,(todo["body"]["proc_counter"]+1,todo["body"]["id"]))
        self.conn.commit()
        cur.close()
        self.fillBodyIds(articlesList,startId)
    
    def __writeArticleUdfs(self, articlesList:list):
        cur = self.conn.cursor()
        for art in articlesList:
            if art.getBodyToWrite()["insert"]:
                for udf in art.getArticle()["udfs"]:
                    cur.execute(databaseExchange.__UDF_INSERT_STATEMENT,(udf[0],article.OBJECT_TYPE, art.getArticle()["body"]["id"],udf[1]))
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
            worklist=list(filter(lambda x: type(x)==article,articlesList[start:start+databaseExchange.SUBSET_LENGTH]))
            headers=list(filter(lambda x: not(x.isInDb()),worklist))
            self.__writeHeaders(headers)
            #headers[0].print()
            print("article headers written and id added")
            #worklist[0].print()
            bodies=list(filter(lambda x: x.isInDb(),worklist))
            self.__writeBodies(bodies)
            print("article bodies written and id added")
            #bodies[0].print()
            self.__writeArticleUdfs(bodies)   
            print("article udfs written")
            start+=databaseExchange.SUBSET_LENGTH

    def fetchCommentIds(self, commentsList:list, startId:int):
        article_body_id_List=list(x.getComment()["data"]["article_body_id"] for x in commentsList)
        article_body_id_tuple=tuple(article_body_id_List)
        commentIds=[]       
        cur = self.conn.cursor()        
        cur.execute(databaseExchange.__COMMENT_ID_FETCH_STATEMENT,(startId,article_body_id_tuple))
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
        cur.execute(databaseExchange.__COMMENT_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0]
        for comm in commentsList:
            if (comm.setComplete()):
                data=comm.getComment()["data"]
                cur.execute(databaseExchange.__COMMENT_STATEMENT,(data["article_body_id"],data["external_id"],data["parent_id"],data["level"],data["body"],data["proc_timestamp"]))
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
                    cur.execute(databaseExchange.__UDF_INSERT_STATEMENT,(udf[0],comment.OBJECT_TYPE, comm.getComment()["data"]["id"],udf[1]))
        self.conn.commit()
        cur.close()   
    
    def writeComments(self, commentsList:list):
        if(type(commentsList)!=list): return False
        start=0
        while start < len(commentsList):
            worklist=list(filter(lambda x: type(x)==comment,commentsList[start:start+databaseExchange.SUBSET_LENGTH]))
            
            # todo filter by not in db (use fetchOldCommentKeys)
            comments=worklist
            
            self.__writeCommentData(comments)
            print("comment data written:",start," - ",start+databaseExchange.SUBSET_LENGTH)
            self.__writeCommentUdfs(comments)
            print("comment udfs written:",start," - ",start+databaseExchange.SUBSET_LENGTH)
            start+=databaseExchange.SUBSET_LENGTH
    
def test():
    testArticle=article()
    testArticle.setHeader({"url":"http://www.google.de","obsolete":False,"source_id":1,"source_date":dt.date(2020,12,1)})
    #testArticle.setBody({"proc_timestamp":dt.datetime(2020,12,2,22,0,33),"headline":"example of headline","body":"testText","proc_counter":2,"id":1})
    #testArticle.setBodyOld()
    testArticle.setBody({"proc_timestamp":dt.datetime.today(),"headline":"example of headline","body":"testText"})
    testArticle.addUdf("author","me")
    testArticle.addUdf("label","smart")
    print("plain article print")
    testArticle.print()
    writer=databaseExchange()
    writer.connect()
    print("last Run= ",writer.fetchLastRun(1))
    writer.logStartCrawl(1)
    writer.writeArticles([testArticle])
    testComment=comment()
    testComment.setData({"article_body_id":141,"level":0,"body":"i'm a comment","proc_timestamp":dt.datetime.today()})
    testComment.addUdf("author","brilliant me")
    testComment.setExternalId((hash("brilliant me"+testComment.getComment()["data"]["body"])))
    print("plain comment print")
    testComment.print()
    writer.writeComments([testComment])
    writer.logEndCrawl()
    todo=writer.fetchTodoList(1)
    for td in todo:
        td.print()
    writer.close()


if __name__ == '__main__':
    print("\n\n")
    print("-------------------------------------------------\n")
    print("Starting databaseExchange showcase here:\n\n")
    print("test deactivated")
    #to reactivateuncomment test()
    #test() functionality spams crap to db. Better use SpiegelOnlineScraper as test unit 