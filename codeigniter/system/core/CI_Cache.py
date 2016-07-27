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
import hashlib
import inspect
import os
import sys
sys.path.insert(0,os.path.dirname(__file__))
import CI_Application
# from CI_Application import CI_Application
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    import thread
except ImportError as e:
    import _thread as thread

from functools import wraps


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
    exp=[]
    exp.append(r"#p\[[\d+]\]\.\w+")
    exp.append(r"#p\[[\d+]\]")
    exp.append(r"#\w+\.\w+")
    exp.append(r"#\w+")
    REGEX_KEY=re.compile(r'|'.join(exp),re.IGNORECASE)
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
        def md5(input):
          m2 = hashlib.md5()
          m2.update(input)
          return str(m2.hexdigest())
        key=(prefix,'$',tpl,'$',str(func),tuple(args),str(kwargs))
        return prefix+'_'+md5(str(key))




    # @staticmethod
    # def get_cache_key_by_dic(prefix,tpl,func,*args,**kwargs):
    #     key=prefix+'$'+func.__name__+'$'
    #     # match= re.findall(r'\#p\[(\d+)\]([^,}]+)?',tpl)
    #     match=CI_Cache.REGEX_KEY.findall(tpl)
    #     # match=[]
    #     # return key
    #     if len(match)<=len(kwargs):
    #         for m in match:
    #             if m[0] in kwargs.keys():
    #                 if isinstance(kwargs[(m[0])],dict):
    #                     if m[1]!='':
    #                         key=key+str(kwargs[(m[0])][m[1][1:]])+'$'
    #                     else:
    #                         key=key+str(kwargs[(m[0])])+'$'
    #                 else:
    #                     key=key+ str(kwargs[(m[0])])+'$'
    #             else:
    #                 continue
    #     return key
    # @staticmethod
    # def get_cache_key_by_args(prefix,tpl,func,args,kwargs,md5=False):
    #     def _md5(input):
    #         m2 = hashlib.md5()
    #         m2.update(input)
    #         return str(m2.hexdigest())
    #     exp=[]
    #     exp.append(r"#p\[[\d+]\]\.\w+")
    #     exp.append(r"#p\[[\d+]\]")
    #     exp.append(r"#\w+\.\w+")
    #     exp.append(r"#\w+")
    #     REGEX_KEY=re.compile(r'|'.join(exp),re.IGNORECASE)
    #     match=REGEX_KEY.findall(tpl)
    #     key=prefix+'$'+func.__name__+'$'
    #     if len(match)==0:
    #         raise  Exception('key must input,example: #id,#p[0].id,#abc.id')
    #     for m in match:
    #         k1=''
    #         k2=''
    #         idx=-1
    #         if m.find('p[')>0:
    #             if str(args[0]).find('instance at')>0:
    #                 idx=int(re.compile(r'#p\[([\d+])\]',re.IGNORECASE).search(m).group(1))+1
    #             else:
    #                 idx=int(re.compile(r'#p\[([\d+])\]',re.IGNORECASE).search(m).group(1))
    #         if m.find(".")>0:
    #             k1,k2=m.split('.')
    #         else:
    #             if k2=='':
    #                 k1=m[1:]
    #         if idx!=-1:
    #             k1=idx
    #             if idx>len(args):
    #                 continue
    #                 pass
    #                 raise  Exception('index out args')
    #             if k2!='':
    #                 if isinstance(args[k1][k2],unicode):
    #                     key+=str( unicode.encode( args[idx][k2],'utf-8','ignore'))+'$'
    #                 else:
    #                     key+=str(args[idx][k2])+'$'
    #             else:
    #                 if isinstance(args[idx],unicode):
    #                     key+=str(unicode.encode( args[idx],'utf-8','ignore'))+'$'
    #                 else:
    #                     key+=str(args[idx])+'$'
    #             continue
    #         else:
    #             if k2!='':
    #                 if isinstance(kwargs[k1][k2],unicode):
    #                     key+=str( unicode.encode( args[idx][k2],'utf-8','ignore'))+'$'
    #                 else:
    #                     key+=str(kwargs[k1][k2])+'$'
    #                 continue
    #             if k1!='':
    #                 if k1 in kwargs.keys():
    #                     if isinstance(kwargs[k1],unicode):
    #                         key+=str( unicode.encode( kwargs[k1],'utf-8','ignore'))+'$'
    #                     else:
    #                         key+=str(kwargs[k1])+'$'
    #                 else:
    #                     raise  Exception('cache key "%s" not found' % k1)
    #                 continue
    #     if md5:
    #         return _md5(key)
    #     else:
    #         return key

    @staticmethod
    def get_func_param_dict(Func,FuncArgs,FuncKwargs):
        d={}
        ArgSpec=inspect.getargspec(Func)
        defualts=ArgSpec[len(ArgSpec)-1]
        keywords=ArgSpec[len(ArgSpec)-2]
        varargs=ArgSpec[len(ArgSpec)-3]
        args=ArgSpec[len(ArgSpec)-4]
        if FuncKwargs==None:
            FuncKwargs={}
        if defualts!=None and len(defualts)>0:
            for i,v in enumerate( args[(len(args)-len(defualts)):]):
                d[v]=defualts[i]
        if len(args)>0 and args[0]=='self':
            args=args[1:]
            FuncArgs=FuncArgs[1:]
        for i,v in enumerate(FuncArgs):
            d[args[i]]=v
        for k,v in FuncKwargs.items():
            d[k]=v
        return d


    @staticmethod
    def get_cache_key_by_args(prefix,tpl,func,args,kwargs,md5=False):
        def _md5(input):
            m2 = hashlib.md5()
            m2.update(input)
            return str(m2.hexdigest())
        exp=[]
        exp.append(r"#\w+\.\w+")
        exp.append(r"#\w+")
        REGEX_KEY=re.compile(r'|'.join(exp),re.IGNORECASE)
        match=REGEX_KEY.findall(tpl)
        key=prefix+'$'+func.__name__+'$'
        data=CI_Cache.get_func_param_dict(func ,args,kwargs)
        params=[]
        for m in match:
            ks=m[1:].split('.')
            if len(ks)==2:
                if ks[0] in data.keys() and ks[1] in data[ks[0]]:
                    if PY2 and isinstance(data[ks[0]][ks[1]],unicode):
                        data[ks[0]][ks[1]]=unicode.encode(data[ks[0]][ks[1]],'utf-8','ignore')
                    key+=str(data[ks[0]][ks[1]])+'$'
                else:
                    raise Exception('cache key error: %s or %s not found'%(ks[0],ks[1]))
            elif len(ks)==1:
                if ks[0] in data.keys():
                    if PY2 and isinstance(data[ks[0]],unicode):
                        data[ks[0]]=unicode.encode(data[ks[0]],'utf-8','ignore')
                    key+=str(data[ks[0]])+'$'
                else:
                    raise Exception('cache key error: %s not found'%(ks[0]))
        # print(key)
        return key




    @staticmethod
    def Cache(prefix='', ttl=3600,key='',op='select',md5=True):
        def handle_func(func):
            @wraps(func)
            def handle_args(*args, **kwargs):
                # print 'xxxxxxx', args,kwargs
                ci=CI_Application.CI
                if ci!=None:
                    if False and  ci.cache.cache_instance==None:
                        ci.logger.error('cache not implment,you can implment it and setting it')
                        return func(*args, **kwargs)
                    else:
                        # op dispatch
                        if key=='' and md5:
                            ckey=CI_Cache.get_cache_key(prefix,key,func,args,kwargs)
                        else:
                            ckey=CI_Cache.get_cache_key_by_args(prefix,key,func,args,kwargs,md5=md5)
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




@CI_Cache.Cache('abc',key='#p[0].index,#p[1],#p[2]',md5=False)
def abc(a,b,c):
    print (a,b,c)




if __name__=='__main__':
    s=time.time()
    for i in xrange(1,10000):
        abc({'index':'adsdf'},2,3)
    print(time.time()-s)
