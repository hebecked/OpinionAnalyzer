#!/usr/bin/python
from datetime import datetime, date, timedelta
import spiegel_scraper as spon
from article import article
from comment import comment
from databaseExchange import databaseExchange
import TemplateScraper
import time

class SponScraper(TemplateScraper.Scraper):

    def __init__(self):
        self.id=1 #set corresponding datasource id here
        pass
   
    def getArticlesList(self, start:date=date(1900,1,1), end:date=date.today()):
        """   
        Parameters
        ----------
        start : date, optional
            DESCRIPTION. The default is date(1900,1,1).
        end : date, optional
            DESCRIPTION. The default is date.today().

        Returns
        -------
        List of corresponding URLs from this source in string format

        """
        #get all articles from archive between corresponding start and end date
        returnList=[]
        num_of_days=(start-end).days
        date_list=[(timedelta(i)+date.today()) for i in range(num_of_days,1)]
        full_list=[]
        for dt in date_list:
            print("fetching date:",dt)
            full_list+=(spon.archive.scrape_html(spon.archive.html_by_date(dt)))
            time.sleep(1) #remove comment for crawler delay
        url_list=list(filter(lambda x: x['is_paid']==False,full_list)) #remove paid aricles without access
        for url in url_list:
            art=article()
            art.setHeader({'source_date':url['date_published'].date(),'source_id':self.id,'url':str(url['url'])})
            returnList+=[art]
        return(returnList)	
	        
    def getArticleDetails(self, art:article):
        time.sleep(1)
        html = spon.article.html_by_url(art.getArticle()['header']['url'])
        content = spon.article.scrape_html(html)
        if('id' in content.keys()):
            art.setBody({'headline':content['headline']['main'],'body':content['text'],'proc_timestamp':datetime.today(),'proc_counter':0})
        #add udfs
        for topic in content['topics']:
            art.addUdf('label',topic)
        for author in content['author']['names']:
            art.addUdf('author',author)
        art.addUdf('date_created',content['date_created'])
        art.addUdf('date_modified',content['date_modified'])
        art.addUdf('date_published',content['date_published'])
        art.freeData=content['id']
        return True
    
    def getWriteArticlesDetails(self, writer:databaseExchange, articlesList:list):
        if(type(articlesList)!=list): return False
        SUBSET_LENGTH=10
        start=0
        while start < len(articlesList):
            for art in articlesList[start:(start+SUBSET_LENGTH)]:
                print("fetching ",art.getArticle()['header']['url'])
                self.getArticleDetails(art)
            writer.writeArticles(articlesList[start:(start+SUBSET_LENGTH)])
            start+=SUBSET_LENGTH
    
    def getCommmentExternalId(self,cmt:spon.comments):
        print("hash:",hash(cmt['user']['username']+cmt['body']))
        return hash(cmt['user']['username']+cmt['body'])

    def flattenComments(self, art:article,comments:list,parent:int,depth=0,start:date=date(1900,1,1),end:date=date.today()):
        returnList=[]
        if type(comments)!=list: 
            return []
        for cmt in comments:
            if (cmt['body']!=None and cmt['user']!=None):
#                print(cmt)
                cmt_id=self.getCommmentExternalId(cmt)
                tmp=comment()
                tmp.setData({"article_body_id":art.getArticle()["body"]["id"],"parent_id":parent,"level":depth,"body":cmt['body'],"proc_timestamp":datetime.today(),"external_id":cmt_id})
                tmp.addUdf("replies",str(len(cmt['replies'])))
                tmp.addUdf("author",cmt['user']['username'])
                tmp.addUdf("created_at",cmt['created_at'])
                if (start<=date.fromisoformat(cmt['created_at'][0:10])<=end):
                    returnList+=[tmp]
                returnList+= self.flattenComments(art,cmt['replies'],cmt_id,depth+1,start,end)
        return returnList

	
    def getCommentsForArticle(self,art:article,start:date=date(1900,1,1),end:date=date.today()): 
        returnList=[]
        if type(art.freeData)==str:
            articleId=art.freeData
        else:    
            articleId=self.getArticleDetails(art.getArticle()['header']['url']).freeData
        comments=spon.comments.by_article_id(articleId)
        returnList+=self.flattenComments(art,comments,None,0,start,end)
        return returnList


    def __del__(self):
        pass

def test():
    SpS=SponScraper()
    test_article=SpS.getArticle("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8")["content"]
    test_comments=SpS.getCommentsForArticle("https://www.spiegel.de/politik/deutschland/angela-merkel-und-ministerpraesidenten-zu-corona-jetzt-stehen-die-laender-unter-zugzwang-a-d0dcad88-ea71-4046-a914-7d7f5069e1c8",
                                            date(2020,11,1),date.today())
    start=date(2020,11,1)
    end=date(2020,11,1)
    for url in SpS.getArticlesList(start,end):
       print(url,end="\n")
    print("\narticle structure:")
    print(test_article.keys())
    print("\ncomment structure:")
    print(test_comments[0].keys())
    print("\nfirst level comments=",len(list(filter(lambda x:x['depth']==0,test_comments))),"\nall comments=",len(test_comments))
   
    SpS.__del__()    

if __name__ == '__main__':
   SpS=SponScraper()
   db=databaseExchange()
   db.connect()
   db.logStartCrawl(SpS.id)
   start=min(db.fetchLastRun(SpS.id).date(),date(2020,12,8))
   end=date.today()
   articleHeaderList=SpS.getArticlesList(start,end)
   db.writeArticles(articleHeaderList)
   todo=db.fetchTodoList(SpS.id)
   SpS.getWriteArticlesDetails(db,todo)
   for art in todo:
       print("fetching comments for article:",art)
       cmts=SpS.getCommentsForArticle(art)
       db.writeComments(cmts)
       time.sleep(1)
   
   db.logEndCrawl()
   db.close()




