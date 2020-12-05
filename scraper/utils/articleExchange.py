import connectDb
from article import article
import datetime as dt

class articleExchange(connectDb.database):
    #__DB_SCHEMA="news_meta_data"
    #__DB_HEADER_TABLE="article_header"
    __HEADER_MIN_STATEMENT="""SELECT MAX(id) FROM news_meta_data.article_header;"""
    __HEADER_STATEMENT="""INSERT INTO news_meta_data.article_header (source_date,obsolete,source_id,url) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __HEADER_ID_FETCH_STATEMENT="""SELECT url, id FROM news_meta_data.article_header WHERE id > %s AND source_id=%s AND source_date=%s;"""

    __BODY_MIN_STATEMENT="""SELECT MAX(id) from news_meta_data.article_body;"""
    __BODY_STATEMENT="""INSERT INTO news_meta_data.article_body (article_id, headline, body, proc_timestamp, proc_counter) VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""
    __BODY_UPDATE_STATEMENT="""UPDATE news_meta_data.article_body set proc_counter=%s where id=%s;"""
    __BODY_ID_FETCH_STATEMENT="""select article_id, max(id) as id from  news_meta_data.article_body where id > %s group by article_id;"""

    __UDF_INSERT_STATEMENT="""INSERT INTO news_meta_data.udf_values (udf_id,object_type,object_id,udf_value) VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING;"""

    def __init__(self):
        super(articleExchange,self).__init__()
        self.__lastBodyWritten=0;
        
    def close(self):
        super(articleExchange,self).close()
    def __del__(self):
        super(articleExchange,self).__del__()
    def connect(self):
        super(articleExchange,self).connect()
        
    def fetchTodoList(sourceId:int):
        #todo
        #get articles (header + body) from db view v_totoCrawl
        #set BodyOld
        pass
    
    def logStartCrawl(sourceId:int):
        #todo
        pass
    def logEndCrawl(sourceId:int):
        #todo
        pass
        

    def fetchArticleIds(self, articlesList:list, startId:int):
        articleIds=[]
        cur = self.conn.cursor()
        for sourcesDates in set((x.getData()["header"]["source_id"],x.getData()["header"]["source_date"]) for x in articlesList):
            cur.execute(articleExchange.__HEADER_ID_FETCH_STATEMENT,tuple([startId]+list(sourcesDates)))
            result = cur.fetchall()
            articleIds+=list(result)
        cur.close()
        return dict(articleIds)
    
    def fetchBodyIds(self, articlesList:list, startId:int):
        bodyIds=[]       
        cur = self.conn.cursor()        
        cur.execute(articleExchange.__BODY_ID_FETCH_STATEMENT,(startId,))
        result = cur.fetchall()
        bodyIds=list(result)       
        return dict(bodyIds)
    
    def __writeHeaders(self, articlesList:list):
        cur = self.conn.cursor()
        cur.execute(articleExchange.__HEADER_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0]
        for art in articlesList:
            if (art.setHeaderComplete()):
                hdr=art.getData()["header"]
                cur.execute(articleExchange.__HEADER_STATEMENT,(hdr["source_date"],hdr["obsolete"],hdr["source_id"],hdr["url"]))
        self.conn.commit()
        # close the communication with the PostgreSQL
        cur.close()
        self.fillHeaderIds(articlesList,startId)

    
    def __writeBodies(self, articlesList:list):
        cur = self.conn.cursor()
        cur.execute(articleExchange.__BODY_MIN_STATEMENT)
        result = cur.fetchall()
        if result[0][0]==None: startId=0
        else: startId=result[0]
        for art in articlesList:
            if (art.setBodyComplete()):
                todo=art.getBodyToWrite()
                #print("todo: ", todo)
                if(todo["insert"]):
                    cur.execute(articleExchange.__BODY_STATEMENT,(todo["body"]["article_id"],todo["body"]["headline"],todo["body"]["body"],todo["body"]["proc_timestamp"],todo["body"]["proc_counter"]+1))
                else:
                    cur.execute(articleExchange.__BODY_UPDATE_STATEMENT,(todo["body"]["proc_counter"]+1,todo["body"]["id"]))
        self.conn.commit()
        cur.close()
        self.fillBodyIds(articlesList,startId)
    
    def __writeUdfs(self, articlesList:list):
        cur = self.conn.cursor()
        for art in articlesList:
            if art.getBodyToWrite()["insert"]:
                for udf in art.getData()["udfs"]:
                    cur.execute(articleExchange.__UDF_INSERT_STATEMENT,(udf[0],article.OBJECT_TYPE, art.getData()["body"]["id"],udf[1]))
        self.conn.commit()
        cur.close()            
    
    def fillHeaderIds(self,articlesList:list, startId: int):
        Ids=self.fetchArticleIds(articlesList,startId)
        for art in articlesList:
            url=art.getData()["header"]["url"]
            if url in Ids.keys():
                art.setHeaderId(Ids[art.getData()["header"]["url"]])
                
    def fillBodyIds(self,articlesList:list, startId: int):
        Ids=self.fetchBodyIds(articlesList,startId)
        for art in articlesList:
            articleId=art.getData()["header"]["id"]
            if articleId in Ids.keys():
                art.setBodyId(Ids[art.getData()["header"]["id"]])    
        
    
    def writeArticles(self, articlesList:list):
        if(type(articlesList)!=list): return False
        SUBSET_LENGTH=100
        start=0
        while start < len(articlesList):
            worklist=list(filter(lambda x: type(x)==article,articlesList[start:start+SUBSET_LENGTH]))
            headers=list(filter(lambda x: not(x.isInDb()),worklist))
            self.__writeHeaders(headers)
            #headers[0].print()
            print("headers written and id added")
            #worklist[0].print()
            bodies=list(filter(lambda x: x.isInDb(),worklist))
            self.__writeBodies(bodies)
            print("bodies written and id added")
            #bodies[0].print()
            self.__writeUdfs(bodies)
            print("udfs written")
            start+=SUBSET_LENGTH



if __name__ == '__main__':
    testArticle=article()
    testArticle.setHeader({"url":"http://www.google.de","obsolete":False,"source_id":1,"source_date":dt.date(2020,12,1)})
    #testArticle.setBody({"proc_timestamp":dt.datetime(2020,12,2,22,0,33),"headline":"example of headline","body":"testText","proc_counter":2,"id":1})
    #testArticle.setBodyOld()
    testArticle.setBody({"proc_timestamp":dt.datetime.today(),"headline":"example of headline","body":"testText"})
    testArticle.addUdf("author","me")
    testArticle.addUdf("label","smart")
    print("plain article print")
    testArticle.print()
    writer=articleExchange()
    writer.connect()
    writer.writeArticles([testArticle])
    writer.close()