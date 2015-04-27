#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import re
import types

from CI_DBActiveRec import CI_DBActiveRec

class CI_DB(object):
    def __init__(self, **kwargs):
        import pymysql
        import DBUtils
        from DBUtils.PooledDB import PooledDB
        if 'app' in kwargs.keys():
            self.app=kwargs['app']
            self.logger=self.app.logger
            del kwargs['app']
        if 'debug' in kwargs.keys():
            self.debug=kwargs['debug']
            del kwargs['debug']
        else:
            self.debug=False
        self.pool=PooledDB(pymysql,**kwargs)

        self.queries=[]



    def get_connection(self):
        # print("get_connection")
        conn= self.pool.dedicated_connection()
        cursor=conn.cursor()
        # cursor.execute('set names utf8')
        # cursor.execute('set autocommit=ON')
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

    def begin(self,conn):
        conn._con.begin()

    def rollback(self,conn):
        conn._con.rollback()

    def commit(self,conn):
        conn._con.commit()

    def close(self,conn):
        conn.close()

    def query(self,sql,param=tuple(),conn=None):
        auto_close=True
        # print(type(conn))
        if type(param) is types.DictType:
            sql,param=self.format(sql,param)
            # print(param)
        if conn==None:
            conn=self.get_connection()
        else:
            auto_close=False
        try:
            cursor=conn.cursor()
            result=cursor.execute(sql,param)
            self.queries.append(sql)
            if len(self.queries)>100:
               del self.queries[0]
            if self.debug:
                self.logger.info(sql)
            if re.compile(r'^\s*(select|show)',re.IGNORECASE).match(sql):
                rows=self.dict_result(cursor)
                return rows
            else:
                return result
        except Exception as  e:
            self.app.logger.error(str(e)+"sql:\n"+sql)
            raise e

        finally:
            try:
                cursor.close()
                if auto_close:
                    conn.close()
                # print("close")
            except UnboundLocalError as ee:
                pass
            except Exception as er:
                self.logger.error(er)
    def execute(self,sql,param=tuple(),conn=None):
        return self.query(sql,param,conn)

    def insert(self, table='', _set=None,conn=None):
       return self.ar(conn).insert(table,_set)

    def update(self, table='', _set=None, where=None, conn=None):
        return self.ar(conn).update(table,_set,where)

    def delete(self, table='', where='',conn=None):
        return self.ar(conn).delete(table,where)

    def ar(self,conn=None):
        kwargs={}
        if conn==None:
            # kwargs['conn']=self.get_connection()
            kwargs['auto_close']=True
            kwargs['app']=self.app
        else:
            kwargs['conn']=conn
            kwargs['auto_close']=False
            kwargs['app']=self.app
        return CI_DBActiveRec(**kwargs)




if __name__=='__main__':

    opts=dict(maxconnections=3,blocking=True,host='172.16.132.230', passwd='root',user="root",database="test")

    db=CI_DB(**opts)


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