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
import thread


class CI_Memory_Cache(object):
    def __init__(self,**kwargs):
        self.cache_dict={}
        self.cache_conf=kwargs['cache']
        self.app=kwargs['app']
        try:
            thread.start_new_thread(self.check)
        except Exception as e:
            self.app.logger.error(e)


    def put(self,key,value,ttl=3600):
        self.cache_dict[key]={'t':int(time.time()),'v':value}
    def get(self,key,ttl):
        if self.cache_dict.has_key(key):
            obj=self.cache_dict[key]
            if int(time.time())- obj['t']>ttl:
                return None
            else:
                return obj['v']
    def check(self):
        while True:
            try:
                if len( self.cache_dict)>int(self.cache_conf['max_count']):
                    self.cache_dict.clear()
                time.sleep(30)
            except Exception as e:
                self.app.logger.error(e)

class CI_Cache(object):

    def __init__(self,**kwargs):
        globals()['ci']=kwargs['app']
        self.cache_conf=kwargs['cache']
        if self.cache_conf['type']=='memory':
            self.cache_instance=CI_Memory_Cache(**kwargs)
        else:
            self.cache_instance=None



    def set_cache(self,cache):
        self.cache_instance=cache


    @staticmethod
    def get_cache_key(prefix,tpl,func,*args):
        key=prefix+'$'+func.__name__
        match= re.findall(r'\#p\[(\d+)\]([^,}]+)?',tpl)
        if len(match)<=len(args):
            for m in match:
                if int(m[0])<len(args):
                    if isinstance(args[int(m[0])],dict):
                        if m[1]!='':
                            key=key+str(args[int(m[0])][m[1][1:]])+'$'
                        else:
                            key=key+str(args[int(m[0])])+'$'
                    else:
                        key=key+ str(args[int(m[0])])+'$'
                else:
                    continue
        return key
    @staticmethod
    def Cache(prefix='', ttl=3600,key=''):
        def handle_func(func):
            def handle_args(*args, **kwargs):
                if 'ci' in globals().keys():
                    if  ci.cache.cache_instance==None:
                        ci.logger.error('cache not implment,you can implment it and setting it')
                        return func(*args, **kwargs)
                    ckey=CI_Cache.get_cache_key(prefix,key,func,*args)
                    obj=ci.cache.cache_instance.get(ckey,ttl)
                    if obj==None:
                        result=func(*args, **kwargs)
                        ci.cache.cache_instance.put(ckey,result,ttl)
                    else:
                        return obj
                    return result
                else:
                    return func(*args, **kwargs)
            return handle_args
        return handle_func




@CI_Cache.Cache('abc',key='#p[0].index,#p[1],#p[2]')
def abc(a,b,c):
    print a,b,c




if __name__=='__main__':
    abc({'index':'adsdf'},2,3)
