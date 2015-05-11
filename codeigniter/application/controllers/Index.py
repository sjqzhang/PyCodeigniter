#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



from codeigniter.system.core.CI_Cache import CI_Cache

class Index:

    def __init__(self,abc=0, *args, **kwargs):
        self.model= kwargs['app'].loader.model('IndexModel')

    @CI_Cache.Cache()
    def index(self):
        print('xxxxxx')
        return "hello world"

    def _abc(self):
        return "_abc"


    def abc(self):
        return "abbc"

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
