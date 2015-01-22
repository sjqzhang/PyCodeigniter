#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



class Index:

    def __init__(self,abc=0, *args, **kwargs):
        pass



    def add(self,a,b):
        return int(a)+int(b)


    def calc(self,expr):
        return eval(expr)


    def ar(self):
        return self.app.db.mquery(self.app.db.get_connection(), 'select * from test')

    def index(self):
        return "hello world"

