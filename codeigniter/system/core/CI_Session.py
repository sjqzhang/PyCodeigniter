#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'
import uuid,time
import threading
from . import PushTraceback
import hashlib
import redis
import gevent
import multiprocessing
import Queue

#from gevent import monkey;gevent.monkey.patch_all(thread=False, socket=False)
class MyLock(object):
    lock = threading.RLock()
    def __enter__(self):
        #print "enter lock"
        MyLock.lock.acquire()
        return self
    def __exit__(self,type, value, traceback):
        #print "out lock"
        MyLock.lock.release()

class ResdisAdaptor(multiprocessing.Process):

    def __init__(self, conf,app):
        multiprocessing.Process.__init__(self)
        self.app = app
        self.conf = conf
        self.expire = int(conf['expire'])
        host , port = conf['host'].split(":")
        # self.geventlocalnamespace =  self.app.cookie.data
        connect_dict = {'host': host,'port':int(port)}
        if conf.get('password',''):
            connect_dict['password'] = conf['conf']
        self.redisConnPool = redis.StrictRedis(**connect_dict)
        self.queue= multiprocessing.Queue(10000)
        self.start()
        


    def set(self,key,value):
        #return r.setex(key,self.expire,value)
        # self.app.logger.info("redis set key:%s,value:%s" % (key,value))
        return self.exec_command("set",(key,self.expire,value) )
        
        

    def get(self,key):
        value  = self.exec_command("get",key )
        #print "get key :%s value %s" % (key,value)
        #value = r.get(key)
        return value

    def exec_command(self,com,v):
        
        print self.queue
        self.queue.put( (com,v) )
        print "put",com,v
        v = self.queue.get()
        print "get",v
        return v
                

    def run(self):
        
        while True:
            try:
                print "start ququq"
                print self.queue
                rsp= None
                va = self.queue.get()
                print "set",com , v 
                com , v = va
                
                if com == "set":
                    key,expire,value = v
                    rsp = self.redisConn.setex(key,self.expire,value)
                if com == "get":
                    key = v
                    rsp = self.redisConn.get(key)
                self.queue.put( rsp )
            except BaseException as e:
                self.app.logger.error( "%s:%s" % ( PushTraceback(),e ) )
                print PushTraceback(),e 


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
        self.data = self.app.cookie.data

        if self.conf['type'] == 'local':
            self.store_porxy = LocalAdaptor(self.conf,self.app)
        elif self.conf['type'] == 'redis':
            self.store_porxy = ResdisAdaptor(self.conf,self.app)
        else:
            raise BaseException("Session storage adaptor must be redis|local ....")        

    def pre_parse_uuid(self):
        try:
            self.cookie = self.app.cookie
            if self.cookie.get('PySessionUUID') <> None:
                return
            self.cookie.set('PySessionUUID',  hashlib.md5("%s_%s" % (uuid.uuid1(),uuid.uuid4()) ).hexdigest() )
        except BaseException as e:
            self.app.logger.error("%s:%s" % ( PushTraceback(),e ))

        
            

    def set(self,key,value):
        try:
            ukey = "%s_%s" %  (self.cookie['PySessionUUID'],key)
            self.store_porxy.set(ukey,value)
        except BaseException as e:
            self.app.logger.error("%s:%s" % ( PushTraceback(),e ))


    def get(self,key):
        try:
            ukey = "%s_%s" %  (self.cookie['PySessionUUID'],key)
            return self.store_porxy.get(ukey)
        except BaseException as e:
            self.app.logger.error("%s:%s" % ( PushTraceback(),e ))
    
    def __getitem__(self,key):
        return self.get(key)

    def __setitem__(self,key,value):
        return self.set(key,value)

    def release(self):
        pass
        
            
            


