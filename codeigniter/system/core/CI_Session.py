#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'
import uuid,time
import threading
# from . import PushTraceback
import hashlib
import redis
import multiprocessing
import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
    import Queue
if PY3:
    import queue as Queue



class ResdisAdaptor(object):

    def __init__(self, conf,app):
        self.app = app
        self.conf = conf
        self.expire = int(conf['expire'])
        host , port = conf['host'].split(":")
        # self.geventlocalnamespace =  self.app.cookie.data
        connect_dict = {'host': host,'port':int(port)}
        if conf.get('password',''):
            connect_dict['password'] = conf['conf']
        self.redis = redis.StrictRedis(**connect_dict)



    def set(self,key,value):
        return self.redis.setex(key,self.expire,value)

    def get(self,key):
        value = self.redis.get(key)
        return value


class MyLock(object):
    lock = threading.RLock()
    def __enter__(self):
        #print "enter lock"
        MyLock.lock.acquire()
        return self
    def __exit__(self,type, value, traceback):
        #print "out lock"
        MyLock.lock.release()

class LocalAdaptor(object):
    class store_data:
        def __init__(self):
            self.name = ""
            self.value = ""
            self.ctime = 0
            self.expire = 0

    def __init__(self, conf,app):
        super(LocalAdaptor, self).__init__()
        self.expire = int(conf['expire'])
        self.store = {}
        self.app = app
        try:
            threading.Thread(target = self._gc, args = ()).start()
        except Exception as e:
            self.app.logger.error(e)


    def set(self,key,value):
        with MyLock() as l:
            v = self.store.get(key,None)
            if v == None:
                v = LocalAdaptor.store_data()
                v.name = key

            v.value = value
            v.ctime = time.time()
            v.expire = self.expire
            self.store[v.name] = v


    def get(self,key):
        with MyLock() as l:
            v = self.store.get(key,None)
            if v == None:
                return None
            else:
                v.ctime = time.time()
                self.store[v.name] = v
                return v.value

    def _gc(self):
        while True:
            try:
                with MyLock() as l:
                    now = time.time()
                    #print "\n\n[GC for local session map]:"
                    #print "\n".join(["key:%s:value:%s,ttl:%s" % (e.name,e.value,e.expire -  now + e.ctime ) for e in self.store.values()])

                    for v in self.store.values():
                        if now - v.ctime > v.expire:
                            del self.store[v.name]
            except BaseException as e:
                self.app.logger.error(e)
            time.sleep(30)



class CI_Session(object):
    """docstring for CI_Session"""
    def __init__(self, **kwargs):
        super(CI_Session, self).__init__()
        self.app = kwargs['app']
        self.conf = kwargs['session']
        self.cookie = self.app.cookie

        if self.conf['type'] == 'local':
            self.store_porxy = LocalAdaptor(self.conf,self.app)
        elif self.conf['type'] == 'redis':
            self.store_porxy = ResdisAdaptor(self.conf,self.app)
        else:
            raise BaseException("Session storage adaptor must be redis|local ....")

    def pre_parse_uuid(self):
        try:
            self.cookie = self.app.cookie
            if self.cookie.get('PySessionUUID') != None:
                return
            self.cookie.set('PySessionUUID',  hashlib.md5("%s_%s" % (uuid.uuid1(),uuid.uuid4()) ).hexdigest() )
        except BaseException as e:
            # self.app.logger.error("%s:%s" % ( PushTraceback(),e ))
            self.app.logger.error(e)




    def set(self,key,value):
        try:
            ukey = "%s_%s" %  (self.cookie['PySessionUUID'],key)
            self.store_porxy.set(ukey,value)
        except BaseException as e:
            self.app.logger.error(e)
            # self.app.logger.error("%s:%s" % ( PushTraceback(),e ))


    def get(self,key):
        try:
            ukey = "%s_%s" %  (self.cookie['PySessionUUID'],key)
            return self.store_porxy.get(ukey)
        except BaseException as e:
            self.app.logger.error(e)
            # self.app.logger.error("%s:%s" % ( PushTraceback(),e ))

    def __getitem__(self,key):
        return self.get(key)

    def __setitem__(self,key,value):
        return self.set(key,value)

    def release(self):
        pass





