#coding=utf-8
#!/usr/bin/python



import pyquery
import time
import urllib2
import urllib
import re


import gevent
from gevent import monkey

monkey.patch_socket()

import sys



class Crawl(object):

    def url_fetch(self, url,data=None):
        html='';
        # print(url)
        try:
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
            }
            if data!=None:
                data=urllib.urlencode(data)
            req = urllib2.Request(
                url =url,
                headers = headers,
                data=data
            )
            html=urllib2.urlopen(req,timeout=15).read()
            charset=re.compile(r'<meta[^>]*charset=[\'\"]*?([a-z0-8\-]+)[\'\"]?[^>]*?>',re.IGNORECASE).findall(html)
            if len(charset) >0:
                if charset[0]=='gb2312':
                    charset[0]='gbk'
                html=unicode(html,charset[0])
            # print(html)
        except Exception:
            pass
        return html

    def url_query(self,url,selector):
        html=self.url_fetch(url)
        return pyquery.PyQuery(selector,html)


if __name__=='__main__':
    crawl=Crawl();

    start=time.time()
    urls=[]
    for a in crawl.url_query("http://xueqiu.com/today/cn",".list_item_tit a"):
        href=pyquery.PyQuery(a).attr('href')
        title=pyquery.PyQuery(a).text()
        if re.match(r'/\d+/\d+',href):
            urls.append({'href':"http://xueqiu.com"+href,'title':title})


    # for u in  urls:
    #     crawl.url_fetch(u['href'])





    # import pymysql
    # pymysql.connect(host="172.16.132.230", user='root', password="root",
    #              database='stock', port=3306, unix_socket=None,
    #              charset='utf-8', sql_mode=None,)
    def save(folder,url):
        import time
        import os

        sd= time.strftime("%Y-%m-%d",time.gmtime())
        text= crawl.url_query(url['href'],'.detail').html()
        title= url['title']
        text=re.sub(r'<br\s*/>',"\r\n",text)
        text=re.sub(r'<p\s+[^>]*?>',"\r\n    ",text)
        text=re.sub(r'</p>',"\r\n",text)
        text=re.sub(r'<\w+[^>]*?>|</\w+>',"",text)
        text=re.sub(r'<!--.*?-->',"",text)
        text=re.sub(r'\$.*?\$',"",text)
        text=re.sub(r'[\r\n]{3,}',"\r\n\r\n",text)
        if not os.path.isdir(folder+sd):
            os.mkdir(folder+sd)
        open(folder+sd+'/'+title.encode('gbk')+'.txt','w').write(text.encode('utf-8'))


    e= [gevent.spawn(save,'I:/xueqiu/',x) for x in urls]

    gevent.joinall(e)

    print(time.time()-start)


