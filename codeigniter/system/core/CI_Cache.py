#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


# def Cache(func):
#     def handle_args(*args, **kwargs):
#         print "begin"
#         return func(*args, **kwargs)
#         print "end"
#     return handle_args


import re
import time
import json

import CI_Application 

try:
    import thread
except ImportError as e:
    import _thread as thread


class CI_Memory_Cache(object):
    def __init__(self,**kwargs):
        self.cache_dict={}
        self.cache_conf=kwargs['cache']
        self.app=kwargs['app']
        try:
            thread.start_new_thread(self.check,())
        except Exception as e:
            self.app.logger.error(e)
    def set(self,key,value,ttl=3600):
        self.put(key,value,ttl)

    def put(self,key,value,ttl=3600):
        self.cache_dict[key]={'t':int(time.time())+ttl,'v':value}
    def get(self,key):
        if key in self.cache_dict.keys():
            obj=self.cache_dict[key]
            if int(time.time())- obj['t']>0:
                return None
            else:
                return obj['v']
    def delete(self,key):
        if key in self.cache_dict.keys():
            del self.cache_dict[key]
    def check(self):
        while True:
            try:
                if len( self.cache_dict)>int(self.cache_conf['max_count']):
                    self.cache_dict.clear()
                else:
                    pass
                time.sleep(30)
            except Exception as e:
                self.app.logger.error(e)


class CI_Cache(object):
    REGEX_KEY=re.compile(r'\#p\[(\w+)\]([^,}]+)?',re.IGNORECASE)
    def __init__(self,**kwargs):
        # globals()['ci']=kwargs['app']
        self.cache_conf=kwargs['cache']
        if self.cache_conf['type']=='memory':
            self.cache_instance=CI_Memory_Cache(**kwargs)
        else:
            self.cache_instance=None

    def set_cache(self,cache):
        self.cache_instance=cache


    def __getattr__(self, item):
        if hasattr(self.cache_instance,item):
            return getattr(self.cache_instance,item)





    @staticmethod
    def get_cache_key(prefix,tpl,func,*args,**kwargs):
        key=prefix+'$'+func.__name__+'$'
        # match= re.findall(r'\#p\[(\d+)\]([^,}]+)?',tpl)
        match=CI_Cache.REGEX_KEY.findall(tpl)
        # match=[]
        # return key
        if len(match)<=len(args):
            for m in match:
                if m[0] in kwargs.keys():
                    if isinstance(kwargs[(m[0])],dict):
                        if m[1]!='':
                            key=key+str(kwargs[(m[0])][m[1][1:]])+'$'
                        else:
                            key=key+str(kwargs[(m[0])])+'$'
                    else:
                        key=key+ str(kwargs[(m[0])])+'$'
                else:
                    continue
        return key
    @staticmethod
    def Cache(prefix='', ttl=3600,key='',op='select'):
        def handle_func(func):
            def handle_args(*args, **kwargs):
                # print args,kwargs
                ci=CI_Application.CI
                if ci!=None:
                    if  ci.cache.cache_instance==None:
                        ci.logger.error('cache not implment,you can implment it and setting it')
                        return func(*args, **kwargs)
                    else:
                        # op dispatch
                        ckey=CI_Cache.get_cache_key(prefix,key,func,*args,**kwargs)
                        if op=='select':
                            obj=ci.cache.cache_instance.get(ckey)
                            if obj==None:
                                result=func(*args, **kwargs)
                                cacheresult=CI_Cache.serial(result)
                                ci.cache.cache_instance.set(ckey,cacheresult,ttl)
                                return result
                            else:
                                obj= CI_Cache.unserial(obj)
                                return obj
                        elif op=='del' or op=='delete' or op=='remove':
                            ci.cache.cache_instance.delete(ckey)
                        elif op=='insert' or op=='update':
                            result=func(*args, **kwargs)
                            cacheresult=CI_Cache.serial(result)
                            ci.cache.cache_instance.set(ckey,cacheresult,ttl)
                            return result
                else:
                    return func(*args, **kwargs)
            return handle_args
        return handle_func

    @staticmethod
    def serial(obj):
        if CI_Application.CI.config['cache']['type']=='memory':
            return obj
        cacheresult=obj
        if isinstance(obj,dict) or isinstance(obj,list) or isinstance(obj,tuple):
            cacheresult='___obj___:'+json.dumps(obj)
        else:
            cacheresult=json.dumps(obj)
        return cacheresult

    @staticmethod
    def unserial(obj):
        if CI_Application.CI.config['cache']['type']=='memory':
            return obj
        if str(obj).startswith('___obj___:'):
            obj=str(obj)[len('___obj___:'):]
        obj=json.loads(obj)
        return obj




@CI_Cache.Cache('abc',key='#p[0].index,#p[1],#p[2]')
def abc(a,b,c):
    print (a,b,c)




if __name__=='__main__':
    abc({'index':'adsdf'},2,3)
