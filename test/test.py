#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import random
import unittest


import os
import sys
sys.path.insert(0,os.path.dirname( os.path.dirname( os.path.abspath( __file__))))

from codeigniter import ci
from codeigniter import CI_Application
from codeigniter import CI_Cache
import time
import threading



class Base(unittest.TestCase):


    def setUp(self):
        self.app=CI_Application(application_path= './',config_file='./config.py')
        # print ci.loader.load_module('../codeigniter/system/core/')
        mdb=ci.loader.cls('CI_DB')(**ci.config.get('mdb'))
        sdb=ci.loader.cls('CI_DB')(**ci.config.get('sdb'))
        # print(sdb)
        ci.set('mdb',mdb)
        ci.set('sdb',sdb)



class TestServer(Base):
    def setUp(self):


        th=threading.Thread(target=ci.start_server)
        th.setDaemon(True)
        th.start()


    def test_app(self):
        port= ci.config.get('server')['port']

        # print ci.request('http://127.0.0.1:8006/index/index')
        print(ci.request('http://127.0.0.1:%s/index/index'%(port)))




class TestDB(Base):

    def setUp(self):
        ci.get('sdb').query('create table IF NOT EXISTS test( id integer autoincreatement,title varchar(128) ,content text)')
        ci.get('mdb').query('''CREATE TABLE  IF NOT EXISTS `test` (
          `id` INT(11) NOT NULL AUTO_INCREMENT,
          `title` VARCHAR(128) DEFAULT NULL,
          `content` TEXT,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB''')

    def tearDown(self):
        ci.get('sdb').query('drop table test')
        ci.get('mdb').query('drop table test')

    def _db(self,db):

        if db.scalar('select count(1) as cnt from test where id=1')['cnt']==0:
            db.insert('test',{'title':'title','content':'content','id':1})
        rows=db.query('select * from test')
        assert len(rows)==1
        db.update('test',{'title':'title','content':'change'},{'id':1})
        rows=db.query('select * from test')
        assert rows[0]['content']=='change'
        db.delete('test',{'id':'1'})
        rows=db.query('select * from test')
        assert len(rows)==0
        with db.tran() as tx:
            if tx.scalar('select count(1) as cnt from test where id=1')['cnt']==0:
                tx.insert('test',{'title':'title','content':'content','id':1})
            rows=tx.query('select * from test')
            assert len(rows)==1
            tx.update('test',{'title':'title','content':'change'},{'id':1})
            rows=tx.query('select * from test')
            assert rows[0]['content']=='change'
            print tx.ar().select('*')._from('test').limit(1,0).get()
            tx.delete('test',{'id':'1'})
            rows=tx.query('select * from test')
            assert len(rows)==0


    def _mysql(self,db):
        with db.tran() as tx:
            tx.insert('test',{'title':'title','content':'content'})
            assert tx.scalar('select max(id) as mid from test')['mid']== tx.scalar('SELECT LAST_INSERT_ID() as last')['last']

        rows=db.select('*')._from('test').limit(1).get()
        assert len(rows)==1


    def _pool(self,db):
        max= ci.config.get('mdb')['maxconnections']
        # for i in range(0, int(max /2) ):
        #     db.get_connection()
        #
        #
        # for i in range(1,max+5):
        #     db.insert('test',{'title':'title','content':'content'})
        #     print db.query('select * from test')

        for i in range(0,max-1):
            # print(i)
            db.get_connection()

        # print('success')

        # db.get_connection()
        for i in range(1,max+5):
            db.insert('test',{'title':'title','content':'content'})
            # print db.query('select * from test')











    def test_db(self):
        self._db(ci.get('sdb'))
        self._db(ci.get('mdb'))

    def test_mysql(self):
        self._mysql(ci.get('mdb'))

    def test_pool(self):
        self._pool(ci.get('mdb'))






class TestCache(Base):

    def test_cache(self):
        ci.cache.set('hello','world')
        world=ci.cache.get('hello')
        assert world=='world'

    @CI_Cache.Cache(key='#a,#b')
    def add(self,a,b):

        return a+b

    def test_cache2(self):
        assert 3==self.add(1,2)



class TestLogging(Base):

    def test_logging(self):
        ci.logger.info('xxxxxx')
        ci.logger.error('xxxxxx')
        ci.logger.warn('xxxxxx')
        ci.logger.debug('xxxxxx')

    def test_logg(self):
        ci.get_logger('log2').info('xxx')




class TestMail(Base):

    def test_mail(self):
        ret=ci.mail.send('easyphp@163.com','unit test','test')
        assert ret==False


class TestLoader(Base):
    def test_loader(self):

        class Add(object):
            def add(self,a,b):
                return a+b

        ci.loader.regcls('add',Add)

        ret= ci.loader.cls('add')().add(2,5)

        assert ret==7

        assert None!=ci.loader.ctrl('index')
class TestRouter(Base):

    def test_router(self):
        status,content= ci.router.route('index','index')
        assert status=='200 OK'


class TestTemplate(Base):
    def test_tpl(self):

        assert 'hello'== ci.tpl.render('Index.html',data={'tpl':'hello'})


class TestRedis(Base):
    def test_redis(self):
        ci.redis.set('a','abc')
        assert  ci.redis.get('a')=='abc'


class TestMemcache(Base):
    def test_redis(self):
        ci.memcache.set('a','abc')
        assert  ci.memcache.get('a')=='abc'
if __name__ == '__main__':
    unittest.main()