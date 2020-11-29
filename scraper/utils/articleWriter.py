import connectDb
from article import article

class articleWriter(connectDb.database):
    #__DB_SCHEMA="news_meta_data"
    #__DB_HEADER_TABLE="article_header"
    __HEADER_STATEMENT="""INSERT INTO news_meta_data.article_header (source_date,obsolete,source,url) VALUES (%s,%s,%s,%s);"""

    def __init__(self):
        super(articleWriter,self).__init__()
    def close(self):
        super()
    def __del__(self):
        super()
    def connect(self):
        super(articleWriter,self).connect()

    def fetchArticleIds(self, articlesList:list):
        pass
    
    def fetchBodyIds(self, articlesList:list):
        pass
    
    def __writeHeaders(self, articlesList:list):
        cur = self.conn.cursor()
        for art in articlesList:
            if (art.setComplete()):
                hdr=art.getData()["header"]
                cur.execute(articleWriter.__HEADER_STATEMENT,(hdr["source_date"],hdr["obsolete"],hdr["source"],hdr["url"]))
        self.conn.commit()
        # close the communication with the PostgreSQL
        cur.close()
        
        
        pass
    
    def __writeBodies(self, articlesList:list):
        pass
    
    def __writeUdfs(self, articlesList:list):
        pass
        
    def writeArticles(self, articlesList:list):
        worklist=list(filter(lambda x: type(x)==article,articlesList))
        headers=list(filter(lambda x: not(x.isInDb()),worklist))
        self.__writeHeaders(headers)
        #__fetchArticleIds
        #__setHeaderIds
        #__writeBodies
        #__fetchBodyIds
        #__setBodyIds
        #__writeUdfs
        pass


if __name__ == '__main__':
    testArticle=article()
    writer=articleWriter()
    writer.connect()
    writer.writeArticles([testArticle])
    writer.close()