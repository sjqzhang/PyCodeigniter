#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

from kazoo.client import KazooClient
from kazoo.client import KazooState

class CI_Zookeeper(object):
    def __init__(self,**kwargs):
        self.zk_conf=kwargs['zookeeper']
        self.app=kwargs['app']
        self.init()

    def init(self):
        self.url=self.zk_conf['url']
        self.user=self.zk_conf['user']
        self.password=self.zk_conf['password']
        self.zk=zk = KazooClient(hosts=self.url,timeout=self.zk_conf['timeout'])
        self.zk.start()
        self.zk.ensure_path(self.zk_conf['path'])
        self.zk.add_listener(self.zk_listener)


    def zk_listener(self,state):
        if state == KazooState.LOST:
            self.init()
        elif state == KazooState.SUSPENDED:
            pass
            # Handle being disconnected from Zookeeper
        else:
            pass
            # Handle being connected/reconnected to Zookeeper



    def get_zk(self):
        return self.zk








if __name__=='__main__':
    zookeeper={
    'url':'172.16.200.233:2181,172.16.200.234:2181,172.16.200.239:2181',
    'path':'/tmp',
    'user':'',
   'password':'',
   'timeout':10
}
    zkconf={'zookeeper':zookeeper,'app':'app'}
    zk=CI_Zookeeper(**zkconf)

