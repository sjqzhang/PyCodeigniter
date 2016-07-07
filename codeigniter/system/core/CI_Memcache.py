#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import memcache



class CI_Memcache(object):
    def __init__(self,**kwargs):
        self.mem_conf=kwargs['memcache']
        self.app=kwargs['app']
        self.mem=None
        self.init()

    def init(self):
        conf=self.app.merge_conf(self.mem_conf)
        self.mem=memcache.Client(**conf)

    def __getattr__(self, item):
        if hasattr(self.mem,item):
            return getattr(self.mem,item)


if __name__=='__main__':
    conf={
    'servers':['172.16.3.92:11211'],
    }
    redisconf={'memcache':conf,'app':'app'}

    r=CI_Memcache(**redisconf)

    r.set('abc','asdfasdfasdf')
    print(r.get('abc'))









