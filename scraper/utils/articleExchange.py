import connectDb
from article import article
import datetime as dt

class articleExchange(connectDb.database):
    #__DB_SCHEMA="news_meta_data"
    #__DB_HEADER_TABLE="article_header"
    __HEADER_STATEMENT="""INSERT INTO news_meta_data.article_header (source_date,obsolete,source_id,url) VALUES (%s,%s,%s,%s);"""
    __HEADER_ID_FETCH_STATEMENT="""SELECT url, id FROM news_meta_data.article_header WHERE source_id=%s and source_date=%s;"""

    def __init__(self):
        super(articleExchange,self).__init__()
    def close(self):
        super()
    def __del__(self):
        super()
    def connect(self):
        super(articleExchange,self).connect()

    def fetchArticleIds(self, articlesList:list):
        articleIDs=[]
        cur = self.conn.cursor()
        for sourcesDates in set((x.getData()["header"]["source_id"],x.getData()["header"]["source_date"]) for x in articlesList):
            cur.execute(articleExchange.__HEADER_ID_FETCH_STATEMENT,sourcesDates)
            result = cur.fetchall()
            articleIDs+=list(result)
        cur.close()
        return dict(articleIDs)
    
    def fetchBodyIds(self, articlesList:list):
        pass
    
    def __writeHeaders(self, articlesList:list):
        #todo add slicing in smaller chunks
        cur = self.conn.cursor()
        for art in articlesList:
            if (art.setHeaderComplete()):
                hdr=art.getData()["header"]
                cur.execute(articleExchange.__HEADER_STATEMENT,(hdr["source_date"],hdr["obsolete"],hdr["source_id"],hdr["url"]))
        self.conn.commit()
        # close the communication with the PostgreSQL
        cur.close()
        
        
        pass
    
    def __writeBodies(self, articlesList:list):
        pass
    
    def __writeUdfs(self, articlesList:list):
        pass
    
    def fillHeaderIds(self,articlesList:list):
        IDs=self.fetchArticleIds(articlesList)
        for article in articlesList:
            article.setHeaderId(IDs[article.getData()["header"]["url"]])
        
    
    def writeArticles(self, articlesList:list):
        worklist=list(filter(lambda x: type(x)==article,articlesList))
        headers=list(filter(lambda x: not(x.isInDb()),worklist))
        #self.__writeHeaders(headers)
        headers[0].print()
        self.fillHeaderIds(worklist)
        worklist[0].print()
        #__setHeaderIds
        #__writeBodies
        #__fetchBodyIds
        #__setBodyIds
        #__writeUdfs
        pass


if __name__ == '__main__':
    testArticle=article()
    testArticle.setHeader({"url":"http://www.google.de","obsolete":False,"source_id":1,"source_date":dt.date.today()})
    testArticle.print()
    writer=articleExchange()
    writer.connect()
    writer.writeArticles([testArticle])
    writer.close()