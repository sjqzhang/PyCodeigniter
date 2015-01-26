#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'




class IndexModel(object):
    def __init__(self,**xx):
        pass

    def index(self):
        return "hello world"

    def search(self):
        return  self.app.db.mquery(self.app.db.get_connection(), 'select * from test')

    def insert(self):
        return self.app.db.insert('test',{'id':"123",'msg':"test"})

    def update(self):
        return self.app.db.update('test',{'msg':"tessdfasdft"},{'id':'123'})

    def delete(self):
        return self.app.db.app.db.delete('test',{'id':'123'})



