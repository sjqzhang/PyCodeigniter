#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import gevent

class IndexModel(object):
    def __init__(self,**xx):
        pass

    def search(self):
         # self.app.db.mquery(self.app.db.get_connection(), "select * from test ")
         # self.app.db.mquery(self.app.db.get_connection(),'SELECT * FROM ggzj ORDER BY RAND() LIMIT 1')


         self.app.db.query( "select * from test ")

         self.app.db.query('SELECT * FROM ggzj ORDER BY RAND() LIMIT 1')


    def ar(self):
        print