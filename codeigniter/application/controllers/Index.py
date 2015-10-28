#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'
from codeigniter import CI


from codeigniter.system.core.CI_Cache import CI_Cache

class Index:

    def __init__(self,abc=0, *args, **kwargs):
        self.data={}
        self.model= kwargs['app'].loader.model('IndexModel')

    @CI_Cache.Cache()
    def index(self):
        print('xxxxxx')
        return "hello world"

    def _abc(self):
        return "_abc"

    @CI_Cache.Cache(prefix='abc',ttl=3,key='#p[0]')
    def abc(self,id="0"):
        return "test cache"

    def _timer(self,callback):
        import datetime
        print('timer:'+ str(datetime.datetime.now()))
        callback(datetime.datetime.now())

    def _timer_callback(self,*args):
        print "callback:", str(args)

    def _shell(self,callback):
        result=''
        callback(result)

    def _cmd(self,cmd=''):
        import os
        return os.popen(cmd).read()

    def search(self):
        return self.model.search()

    def insert(self):
       return  self.model.insert()

    def update(self):
        return  self.model.update()

    def delete(self):
        return  self.model.delete()

    def ar(self):
        return self.model.ar()

    def tran(self):
        return self.model.tran()
