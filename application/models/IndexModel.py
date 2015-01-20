#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


class IndexModel(object):
    def __init__(self,**xx):
        pass

    def search(self):
       print  self.app.db.query("select * from test")


    def ar(self):
        print