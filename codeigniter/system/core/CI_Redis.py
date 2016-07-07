#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import redis



class CI_Redis(object):
    def __init__(self,**kwargs):
        self.redis_conf=kwargs['redis']
        self.app=kwargs['app']
        self.redis=None
        self.pool=None
        self.init()

    def init(self):
        conf=self.app.merge_conf(self.redis_conf,{'db':0,'password':None,'port':6379,'cls':'StrictRedis','max_connections':10})
        cls= conf.pop('cls')
        # max_connections=conf.pop('max_connections')
        self.pool=redis.ConnectionPool(**conf)
        self.redis=getattr(redis,cls)(connection_pool=self.pool)
        # self.redis=getattr(redis,cls)(**conf)

    def __getattr__(self, item):
        if hasattr(self.redis,item):
            return getattr(self.redis,item)


if __name__=='__main__':
    conf={
    'host':'172.16.3.92',
    'port':6379,
#    'db':0,
   'password':None,
    }
    redisconf={'redis':conf,'app':'app'}

    r=CI_Redis(**redisconf)

    (r.set)('asdf','asdfasdfasdf')









