#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import re
import types

class CI_DB(object):
    def __init__(self, **kwargs):
        import pymysql
        import DBUtils
        from DBUtils.PooledDB import PooledDB
        if kwargs.has_key('app'):
            self.app=kwargs['app']
            self.logger=self.app.logger
            del kwargs['app']
        self.pool=PooledDB(pymysql,**kwargs)

        self.queries=[]


    def get_connection(self):
        conn= self.pool.dedicated_connection()
        cursor=conn.cursor()
        cursor.execute('set names utf8')
        cursor.execute('set autocommit=ON')
        cursor.close()
        return conn

    def last_query(self):
        if len(self.queries)>0:
            return self.queries[-1]

    def format(self,sql,param):
        m=re.findall(r"{\w+}",sql,re.IGNORECASE|re.DOTALL)
        v=list()
        for i in m:
            key,num=re.subn(r"^'?{|}'?$",'',i)
            v.append(param[key])
            sql=sql.replace(i,'%s')
        return sql,tuple(v)

    def dict_result(self,cursor):
        rows=cursor.fetchall()
        desc=cursor.description
        title=[]
        result=[]
        idx=0
        for i in desc:
            title.append({idx:i[0]})
            idx=idx+1
        for row in rows:
            row2={}
            for i in title:
                for k in i.keys():
                    row2[i[k]]=row[k]
            result.append(row2)
        return result

    def query(self,sql,param=tuple()):
        if type(param) is types.DictType:
            sql,param=self.format(sql,param)
            # print(param)
        conn=self.get_connection()
        try:
            cursor=conn.cursor()
            result=cursor.execute(sql,param)
            self.queries.append(sql)
            if re.compile(r'^\s*(select|show)',re.IGNORECASE).match(sql):
                rows=self.dict_result(cursor)
                return rows
            else:
                return result
        except Exception,e:
            print(e)

        finally:
            try:
                cursor.close()
                conn.close()
            except UnboundLocalError,ee:
                pass




if __name__=='__main__':

    opts=dict(maxconnections=3,blocking=True,host='172.16.132.230', passwd='root',user="root",database="test")

    db=CI_Database(**opts)


    rows=db.query("select * from test")



    for row in rows:
        print(row[1])

    print(rows)


    db.query("""INSERT INTO test.test
	(id,
	msg
	)
	VALUES
	('4',
	'msg'
	);""")