#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import redis


class CI_Redis(object):
    def __init__(self,**kwargs):
        self.redis_conf=kwargs['redis']
        self.app=kwargs['app']
        self.redis=None
        self.init()

    def init(self):
        self.redis=redis.Redis(host=self.redis_conf['host'],port=self.redis_conf['port'],password=self.redis_conf['password'],db=self.redis_conf['db'])

    def __getattr__(self, item):
        if hasattr(self.redis,item):
            return getattr(self.redis,item)


if __name__=='__main__':
    conf={
    'host':'172.16.3.92',
    'port':6379,
    'db':0,
   'password':None,
    }
    redisconf={'redis':conf,'app':'app'}

    r=CI_Redis(**redisconf)

    (r.set)('asdf','asdfasdfasdf')









