#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import re
import pyquery
import sys
import json
import hashlib
import platform

class XueQiu(object):


    def __init__(self,**kwargs):
        pass
        self.db=None



    def load_url(self):
        crawl=self.app.loader.helper('Crawl')
        urls=[]
        url="http://xueqiu.com/today/cn"

        dbconf=self.app.config['db']
        dbconf['database']='stock'
        self.db=self.app.loader.cls('CI_DBActiveRec')(**dbconf)

        for a in crawl.url_query(url,".list_item_tit a"):
            href=pyquery.PyQuery(a).attr('href')
            title=pyquery.PyQuery(a).text()

            if href!=None and re.match(r'/\d+/\d+',href):
                urls.append({'href':"http://xueqiu.com"+href,'title':title,'selector':'.detail','type':"1"})

        for u in urls:
            if platform.system()=='Windows':
                self.save('I:/xueqiu/',u)
            else:
                self.save('/media/sf_idriver/xueqiu/',u)



    def load_news_urls(self):
        dbconf=self.app.config['db']
        dbconf['database']='stock'
        self.db=self.app.loader.cls('CI_DBActiveRec')(**dbconf)
        urls=[]
        url="http://www.gov.cn/xinwen/xw_rd.htm"
        crawl=self.app.loader.helper('Crawl')
        for a in crawl.url_query(url,".pubListBox01 li a"):
            href=pyquery.PyQuery(a).attr('href')
            title=pyquery.PyQuery(a).text()
            # print(href,title)
            urls.append({'href':"http://www.gov.cn/xinwen/"+href,'title':title,'selector':'#printContent',"type":"2"})


        for u in urls:
            if platform.system()=='Windows':
                self.save('I:/xueqiu/',u)
            else:
                self.save('/media/sf_idriver/xueqiu/',u)






    def load_json_url(self):
        crawl=self.app.loader.helper('Crawl')

        for i in xrange(1,5):
            url='http://xueqiu.com/statuses/topic.json?simple_user=1&filter_text=1&topicType=5&page=%s&_=1421806349443'%i
            data=crawl.url_fetch(url)
            data= json.loads(data,"utf-8")
            print(data)





    def save(self, folder,url):
        crawl=self.app.loader.helper('Crawl')
        import time
        import os
        md5=hashlib.md5(url['href'].encode('utf-8')).hexdigest()
        row=self.db.query("select 1 from ebook where md5='%s'"%md5)
        if len(row)>0:
            return;
        sd= time.strftime("%Y-%m-%d",time.gmtime())
        text= crawl.url_query(url['href'],url['selector']).html()
        title= url['title']
        text=re.sub(r'<br\s*/>',"\r\n",text)
        text=re.sub(r'<p\s+[^>]*?>',"\r\n    ",text)
        text=re.sub(r'</p>',"\r\n",text)
        text=re.sub(r'<\w+[^>]*?>|</\w+>',"",text)
        text=re.sub(r'<!--.*?-->',"",text)
        text=re.sub(r'\$.*?\$',"",text)
        text=re.sub(r'%',"%%",text)
        title=re.sub(r'%',"%%",title)
        title=re.sub(r'\\|\/|\:|\*|\?|\"|\<|>|\|',"",title)
        text=re.sub(r'[\r\n]{3,}',"\r\n\r\n",text)

        data={'title':title.encode('utf-8'),'content':text.encode('utf-8'),'md5':md5,'cdate':sd,'url':url['href'],'type':url['type']}

        if len(row)==0:
            # print(data)
            self.db.insert('ebook',data)
            if not os.path.isdir(folder+sd):
                os.mkdir(folder+sd)
            try:
                if platform.system()=='Windows':
                    open(folder+sd+'/'+title.encode('gbk')+'.txt','w').write(text.encode('utf-8'))
                else:
                    open(folder+sd+'/'+title.encode('utf-8')+'.txt','w').write(text.encode('utf-8'))
            except Exception,e:
                print(e)
                pass




if __name__=='__main__':
    pass