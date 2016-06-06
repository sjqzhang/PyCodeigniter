#coding=utf-8
#!/usr/bin/python




import urllib2
import urllib
import re
from  urlparse import urlparse




class Crawl(object):


    def parse_url(self,url):

        url_info=urlparse(url)
        host=url_info.scheme+'://'+url_info.netloc
        relative=host
        if len(url_info.path)>0 and url_info.path.rindex('/')>0:
            relative=host + url_info.path[0: url_info.path.rindex('/')]
        return host,relative


    def url_fetch(self, url,data=None):
        import pyquery
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
            absolute_url,relative_url=self.parse_url(url)
            html=re.sub(r'src="/','src="'+absolute_url+'/',html)
            html=re.sub(r'href="/','href="'+absolute_url+'/',html)
            html=re.sub(r'src="(?!http)([^"]*)"','src="'+relative_url+'/\\1"',html)
            html=re.sub(r'src=\'(?!http)(?!#)([^\']*)\'','src=\''+relative_url+'\\1\'',html)
            html=re.sub(r'href=\'(?!http)(?!#)([^\']*)\'','href=\''+relative_url+'\\1\'',html)
            html=re.sub(r'href="(?!http)([^"]*)"','href="'+relative_url+'/\\1"',html)

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
        import pyquery
        html=self.url_fetch(url)
        return pyquery.PyQuery(selector,html)

    def pq(self,obj):
        import pyquery
        return pyquery.PyQuery(obj)

    def table(self,obj):
        import collections
        rows=[]
        table=self.pq(obj)
        for tr in pyquery.PyQuery('tr',table):
            row=collections.OrderedDict()
            ri=0
            for td in pyquery.PyQuery('td',tr):
                row[ri]=pyquery.PyQuery(td).text()
                ri=ri+1
            if len(row)>0:
                rows.append(row)
        return rows



if __name__=='__main__':
    pass
    import pyquery
    crawl=Crawl();
    rows= crawl.table(table)

    # for row in rows:
    #     print row.get(3)






    # href=crawl.url_query('http://quote.eastmoney.com/stocklist.html','.quotebody').html()
    # print(href)
  #   href=crawl.url_query('http://quote.eastmoney.com/stocklist.html','.quotebody li a')
  #   d={}
  #   sql='''INSERT INTO stock.stock_code
	# (stockno,
	# NAME
	# )
	# VALUES
	# ('%s',
	# '%s'
	# );
  # '''
  #   for url in href:
  #       text=crawl.pq(url).text()
  #       code=re.findall(r'\d{6}', crawl.pq(url).text())
  #       name=text.replace('('+code[0]+')','')
  #       # print(name)
  #       # print(code[0])
  #       # d[code[0][0:3]]='abc'
  #       print(sql % (code[0],name))
  #
  #   print(d.keys())
    # aa=""
    #
    # url_info='http://www.baidu.com'
    #
    # print crawl.url_fetch('http://test.meizu.com/')
    # print crawl.parse_url(url_info)
    #
    # start=time.time()
    # urls=[]
    # for a in crawl.url_query("http://xueqiu.com/today/cn",".list_item_tit a"):
    #     href=pyquery.PyQuery(a).attr('href')
    #     title=pyquery.PyQuery(a).text()
    #     if re.match(r'/\d+/\d+',href):
    #         urls.append({'href':"http://xueqiu.com"+href,'title':title})


    # for u in  urls:
    #     crawl.url_fetch(u['href'])





    # import pymysql
    # pymysql.connect(host="172.16.132.230", user='root', password="root",
    #              database='stock', port=3306, unix_socket=None,
    #              charset='utf-8', sql_mode=None,)
    # def save(folder,url):
    #     import time
    #     import os
    #
    #     sd= time.strftime("%Y-%m-%d",time.gmtime())
    #     text= crawl.url_query(url['href'],'.detail').html()
    #     title= url['title']
    #     text=re.sub(r'<br\s*/>',"\r\n",text)
    #     text=re.sub(r'<p\s+[^>]*?>',"\r\n    ",text)
    #     text=re.sub(r'</p>',"\r\n",text)
    #     text=re.sub(r'<\w+[^>]*?>|</\w+>',"",text)
    #     text=re.sub(r'<!--.*?-->',"",text)
    #     text=re.sub(r'\$.*?\$',"",text)
    #     text=re.sub(r'[\r\n]{3,}',"\r\n\r\n",text)
    #     if not os.path.isdir(folder+sd):
    #         os.mkdir(folder+sd)
    #     open(folder+sd+'/'+title.encode('gbk')+'.txt','w').write(text.encode('utf-8'))


    # e= [gevent.spawn(save,'I:/xueqiu/',x) for x in urls]
    #
    # gevent.joinall(e)

    # print(time.time()-start)


