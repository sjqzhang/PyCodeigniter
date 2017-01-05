#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import re
import types
import collections
import sys
import os
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
sys.path.insert(0,os.path.dirname(__file__))


from CI_DBActiveRec import CI_DBActiveRec
from CI_Util import OrderedDict


import time
from threading import Lock
import threading
import time
if PY2:
    from  Queue import Queue
if PY3:
    from queue import Queue
class Pool(object):
    def __init__(self,creator,**kwargs):
        # self.mutex=Lock()
        self.creator=creator
        self.idle=[]
        if 'blocking' in kwargs.keys():
            self.blocking=kwargs['blocking']
            del kwargs['blocking']
        else:
            self.blocking=True
        if 'maxconnections' in kwargs.keys():
            self.maxconnections=kwargs['maxconnections']
            del kwargs['maxconnections']
        else:
            self.maxconnections=1
        self._kwargs=kwargs
        self.pool=Queue(self.maxconnections)

        for i in range(self.maxconnections):
            self.pool.put(self.create_connection())
        daemon=threading.Thread(target=self._check_alive)
        daemon.setDaemon(True)
        daemon.start()


    def ping(self,conn):
        try:
            cursor= conn.cursor()
            cursor.execute('select 1')
            row=cursor.fetchall()
            if len(row)>0:
                return True
            else:
                return False
        except Exception as er:
            return False
        return True

    def _check_alive(self):
        while True:
            try:
                size=self.pool.qsize()
                for i in range(0,size):
                    conn=self.get_connection()
                    if hasattr(conn._con, 'ping') and callable(conn._con.ping):
                        try:
                            conn._con.ping()
                            conn.close()
                        except Exception as er:
                            conn=self.create_connection()
                            self.pool.put(conn)
                    else:
                        if self.ping(conn):
                            conn.close
                        else:
                            conn=self.create_connection()
                            self.pool.put(conn)
                time.sleep(60)
            except Exception as er:
                pass

    # def get_connection(self):
    #     conn=None
    #     try:
    #         conn=self.pool.get_nowait()
    #     except Exception as er:
    #         conn=None
    #     if conn!=None:
    #         return conn
    #     else:
    #         def _wait():
    #             while True:
    #                 try:
    #                     conn=self.pool.get_nowait()
    #                     return conn
    #                 except Exception as er:
    #                     time.sleep(0.1)
    #                     pass
    #
    #         daemon=threading.Thread(target=_wait)
    #         daemon.setDaemon(True)
    #         daemon.start()
    #         daemon.join()
    #         return conn




    def get_connection(self,deep=0):
        try:
            while True:
                try:
                    conn=self.pool.get_nowait()
                except Exception as er:
                    conn=None
                if conn==None:
                    time.sleep(0.2)
                    deep=deep+1
                    if deep>60:
                        raise Exception('The connection to the database resources are exhausted!')
                    return self.get_connection(deep)
                else:
                    return conn

        except Exception as er:
            raise Exception(er)

    # def reconnect(self,conn):
    #     pass

    def create_connection(self):
        class Connection(object):
            def __init__(self,con,pool):
                self.pool=pool
                self._con=con
                self.idle=False
            def close(self):
                try:
                    self.pool.pool.put(self)
                except Exception as er:
                    pass
            def __getattr__(self, item):
                if hasattr(self._con,item):
                    return getattr(self._con,item)
        conn= Connection(self.creator.connect(**self._kwargs),self)
        return conn













class CI_DB(object):
    def __init__(self, **kwargs):
        if 'app' in kwargs.keys():
            self.app=kwargs['app']
            self.logger=self.app.logger
            del kwargs['app']
        if 'type' in kwargs.keys():
            del kwargs['type']
        if 'debug' in kwargs.keys():
            self.debug=kwargs['debug']
            del kwargs['debug']
        else:
            self.debug=False
        if 'autocommit' in kwargs.keys():
            self.autocommit=kwargs['autocommit']
        else:
            self.autocommit=True
        if 'creator' in kwargs.keys():
            self.creator=kwargs['creator']
            del kwargs['creator']
        else:
            self.creator='pymysql'
        self.creator_mod=None
        try:
            self.creator_mod=__import__(self.creator)
        except Exception as er:
            self.logger.error(er)

        # self.pool=Pool(self.creator_mod,**kwargs)
        # self.logger.info('DB pool:CI_DB.Pool')
        try:
            from DBUtils.PooledDB import PooledDB
            self.pool=PooledDB(self.creator_mod,**kwargs)
            self.logger.info('DB pool:DBUtils.PooledDB')
        except:
            self.pool=Pool(self.creator_mod,**kwargs)
            self.logger.info('DB pool:CI_DB.Pool')


        self.queries=[]



    def get_connection(self):
        # print("get_connection")
        if hasattr(self.pool,'get_connection'):
            conn= self.pool.get_connection()
        else:
            conn= self.pool.dedicated_connection()
        return conn

    def get_raw_connection(self):
        return self.get_connection()._con

    def last_query(self):
        if len(self.queries)>0:
            return self.queries[-1]

    def escape_str(self, string, like = False):
        if isinstance(string, dict):
            for key,val in string.iteritems():
                string[key] = self.escape_str(val, like)
            return string

        string = ''.join({'"':'\\"', "'":"\\'", "\0":"\\\0", "\\":"\\\\"}.get(c, c) for c in string)

        # escape LIKE condition wildcards
        if like == True:
            string = string.replace('%', '\\%')
            string = string.replace('_', '\\_')

        return string



    def sql_format(self,sql,param):
        m=re.findall(r"{\w+}|\:\w+",sql,re.IGNORECASE|re.DOTALL)
        v=list()
        def lcmp(x,y):
            if len(x)>len(y):
                return -1
            else:
                return 1
        ks=[]
        for i in m:
            key,num=re.subn(r"^'?{|}'?$|^\:",'',i)
            sql=sql.replace(i,self.escape_str(param[key]))

        return sql

    def format(self,sql,param):
        m=re.findall(r"{\w+}|\:\w+",sql,re.IGNORECASE|re.DOTALL)
        v=list()
        def lcmp(x,y):
            if len(x)>len(y):
                return -1
            else:
                return 1
        ks=[]
        for i in m:
            key,num=re.subn(r"^'?{|}'?$|^\:",'',i)
            v.append(param[key])
            ks.append(i)

        ks.sort(lcmp)
        for i in ks:
            sql=sql.replace(i,'%s')
        if self.creator=='sqlite3':
            sql=sql.replace("'%s'",'?')
            sql=sql.replace("%s",'?')
        else:
            sql=sql.replace("'%s'",'%s')

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
            # row2=collections.OrderedDict()
            row2=OrderedDict()
            for i in title:
                for k in i.keys():
                    row2[i[k]]=row[k]
            result.append(row2)
        return result

    def begin(self,conn):
        if hasattr(conn._con,'begin') and callable(getattr(conn._con,'begin')):
            conn._con.begin()

    def rollback(self,conn):
        conn._con.rollback()

    def commit(self,conn):
        if conn._con!=None:
            conn._con.commit()

    def close(self,conn):
        conn.close()

    def batch(self,sql,param=list(),split=';',conn=None,auto_commit=True):
        if not isinstance(param,list):
            raise Exception('param must be list')
        batch_sqls=[]
        values=[]
        for row in param:
            _sql,vs=self.format(sql,row)
            for _v in vs:
                values.append(_v)
            batch_sqls.append(_sql)
        full_sql=split.join(batch_sqls)
        return self.query(full_sql,tuple(values),conn,auto_commit)




    def query(self,sql,param=tuple(),conn=None,auto_commit=True):
        # auto_commit=True
        # print(type(conn))
        if param==None:
            param=tuple()
        if isinstance(param,dict) and len(param)>0:
            sql,param=self.format(sql,param)
            # print(param)
        if self.debug:

            if PY2 and isinstance(sql,unicode):
                sql=unicode.encode(sql,'utf-8','ignore')
            self.logger.info(sql)
        auto_close_connection=False
        if conn==None:
            conn=self.get_connection()
            auto_close_connection=True
        # else:
        #     auto_commit=False
        try:
            cursor=conn.cursor()
            if len(param)>0:
                result=cursor.execute(sql,param)
            else:
                result=cursor.execute(sql)
            self.queries.append(sql)
            if auto_commit and self.creator=='sqlite3':
                self.commit(conn)
            if len(self.queries)>100:
               del self.queries[0]
            if re.compile(r'^\s*(select|show)',re.IGNORECASE).match(sql):
                rows=self.dict_result(cursor)
                return rows
            else:
                return result
        except Exception as e:
            keys=['gone away','connection','server','lost']
            for key in keys:
                if str(e).lower().find(key)!=-1:
                    if hasattr(self.pool,'reconnect'):
                        self.pool.reconnect(conn)
                    break
            # if auto_commit and  self.creator=='sqlite3':
            #     self.rollback(conn)
            if PY2 and isinstance(sql,unicode):
                sql=unicode.encode(sql,'utf-8','ignore')
            self.app.logger.error(str(e)+"sql:\n"+sql)
            raise e

        finally:
            try:
                try:
                    cursor.close()
                except Exception as er:
                    pass
                if auto_close_connection or auto_commit:
                    conn.close()

                # print("close")
            except UnboundLocalError as ee:
                pass
            except Exception as er:
                self.logger.error(er)
    def execute(self,sql,param=tuple(),conn=None,auto_commit=True):
        return self.query(sql,param,conn,auto_commit)

    def insert(self, table='', _set=None,conn=None):
       return self.ar(conn).insert_safe(table,_set)

    def update(self, table='', _set=None, where=None, conn=None):
        return self.ar(conn).update_safe(table,_set,where)

    def delete(self, table='', where='',conn=None):
        return self.ar(conn).delete(table,where)

    def scalar(self,sql,param=tuple(),conn=None,auto_commit=True):
        rows=self.query(sql,param,conn,auto_commit)
        if isinstance(rows,list) and len(rows)>0:
            return rows[0]
        else:
            return None

    def tran(self,conn=None):

        class Tran():
            def __init__(self,db,conn=None):
                self._db=db
                if conn==None:
                    self.conn=self._db.get_connection()
                else:
                    self.conn=conn
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type==None:
                    self._db.commit(self.conn)
                else:
                    self._db.rollback(self.conn)
                self.conn.close()

            def __enter__(self):
                self._db.begin(self.conn)
                return self

            def __getattr__(self, item):
                return getattr(self._db,item)

            def query(self,sql,param=tuple()):
                return self._db.query(sql,param,self.conn,auto_commit=False)
            def execute(self,sql,param=tuple()):
                return self.query(sql,param,self.conn,auto_commit=False)
            def scalar(self,sql,param=tuple()):
                return self._db.scalar(sql,param,self.conn,auto_commit=False)
            def insert(self, table='', _set=None):
                return self._db.insert(table,_set,self.conn)
            def update(self, table='', _set=None, where=None):
                return self._db.update(table,_set,where,self.conn)
            def delete(self, table='', where=''):
                return self._db.delete(table,where,self.conn)
            def ar(self,conn=None):
                return self._db.ar(self.conn)

        return Tran(self,conn)



    def ar(self,conn=None):
        kwargs={}
        ar= CI_DBActiveRec(**kwargs)
        if conn==None:
            ar.auto_close=True
        ar.db=self
        ar.conn=conn
        return ar


    def __getattr__(self,attr):
        ar=self.ar()
        self.db=self
        # ar.conn=self.get_connection()
        if hasattr(ar,attr):
            return getattr(ar,attr)
        return None

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