#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


from codeigniter import ci
from codeigniter import CI_Cache

class Index:


    def index(self,req,resp):
        return "hello world"

    def favicon(self,req,resp):
        return "favicon"

    def test_task(self,req,resp):
        import datetime
        print('timer:'+ str(datetime.datetime.now()))

    def test_db(self,req,resp):
        row= ci.db.query('select 1')
        print(ci.db.scalar('select 1'))
        # ci.db.insert('tablenname',{'fieldname1':'value1','fieldname2':'value2'})
        # ci.db.update('tablenname',{'fieldname1':'value1','fieldname2':'value2'},{'condition':'conditionvalue'})
        # ci.db.select('*')._from('test').limit(10).get()
        return row

    def test_config(self,req,resp):
        print(ci.config)

    def test_loader(self,req,resp):
        ci.loader.helper('your helper')
        ci.loader.library('your library')
        ci.loader.model('your model')




    #how to create different instance ?
    def test_loader_instances(self,req,resp):
        #how to connect to different db ?

        db2=ci.loader.cls('CI_DB')(ci.config['db2']) # how to create different db instance and save it into ci
        ci.set('db2',db2)  # save it  into ci
        print(ci.get('db2').query('select 1'))

        #how to log to different file ?

        logger2=ci.loader.cls('CI_Logger')(ci.config['log2']) # how to create different db instance and save it into ci
        ci.set('logger2',logger2)  # save it  into ci
        print(ci.get('logger2').info('asdfasdfas'))

        #The rest may be deduced by analogy


    def test_mail(self,req,resp):
        ci.mail.send(['test@abc.com'],'test','message')

    @CI_Cache.Cache(prefix='test_auto_cache',ttl=3600,key='#id,#name')
    def test_auto_cache(self,id=0,name='hello'): #auto cache result
        ci.cacche.set('abc',"hello world")
        return ci.cache.get('abc')
    def test_cache(self,req,resp):
        ci.cacche.set('abc',"hello world")
        return ci.cache.get('abc')

    def test_logger(self,req,resp):
        ci.logger.info('Hello World')

    def test_redis(self,req,resp):
        self.redis.set('test','test') # see redis api
        return self.redis.get('test')

    def test_memcache(self,req,resp):
        self.memcache.set('test','test') # see memcache api
        return self.memcache.get('test')

    def test_tpl(self,req,resp): #template
        return ci.tpl.render('template.html',[{'sNo':'123456','chinese':67,'math':90,'englist':85},\
            {'sNo':'123456','chinese':80,'math':96,'englist':85}])
