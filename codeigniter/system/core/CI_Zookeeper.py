#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

from kazoo.client import KazooClient
from kazoo.client import KazooState
import threading
import time


class CI_Zookeeper(object):
    def __init__(self,**kwargs):
        self.zk_conf=kwargs['zookeeper']
        self.app=kwargs['app']
        self.election=None
        self._is_leader=False
        self.timeout=10
        self.init()




    def init(self):
        self.url=self.zk_conf['url']
        self.user=self.zk_conf['user']
        self.password=self.zk_conf['password']
        self.timeout=self.zk_conf['timeout']
        self.zk=zk = KazooClient(hosts=self.url,timeout=self.zk_conf['timeout'])
        self.zk.start()
        self.zk.ensure_path(self.zk_conf['path'])
        self.election = zk.Election(self.zk_conf['path'])
        self.zk.add_listener(self.zk_listener)
        threading.Thread(target=self._noblock).start()
        time.sleep(0.2)


    def zk_listener(self,state):
        if state == KazooState.LOST:
            self.init()
        elif state == KazooState.SUSPENDED:
            pass
            # Handle being disconnected from Zookeeper
        else:
            pass
            # Handle being connected/reconnected to Zookeeper

    def _jump(self):
        while True:
            self._is_leader=True
            time.sleep(0.5)

    def _noblock(self):
        while True:
            self.election.run(self._jump)
            self._is_leader=False


    def is_leader(self):
        # time.sleep(self.timeout+2)
        return self._is_leader

    def is_leader2(self,callback,*args,**kwargs):
        self.election.run(callback,*args,**kwargs)

    def __getattr__(self, item):
        if hasattr(self.zk,item):
            return getattr(self.zk,item)

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
    import time
    def  test():
        time.sleep(5)
        print('hello wlorl')
        time.sleep(50)
    # time.sleep(2)
    while True:
        print(zk.is_leader())
        time.sleep(1)
    # time.sleep(50)





#
# from kazoo.client import KazooClient
# import time
# import uuid
#
# import logging
# logging.basicConfig()
#
# my_id = uuid.uuid4()
#
# def leader_func():
#     print "I am the leader {}".format(str(my_id))
#     while True:
#         print "{} is working! ".format(str(my_id))
#         time.sleep(3)
#
# zk = KazooClient(hosts='127.0.0.1:2181')
# zk.start()
#
# election = zk.Election("/electionpath")
#
# # blocks until the election is won, then calls
# # leader_func()
# election.run(leader_func)
#
# zk.stop()
