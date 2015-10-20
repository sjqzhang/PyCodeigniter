#!/usr/bin/env python
# -*- coding:utf8 -*-
import gevent
from gevent.local import local

from . import PushTraceback
import gevent

class CookieData:
    def __init__(self):
        self.name = ""
        self.value = ""
        self.maxage = ""
        self.path = "/"
        self.domain = ""
        self.secure = False
        self.isPre = True

    def __str__(self):
        if self.isPre:
            return ""
        cookie = "%s=%s" % ( self.name , self.value )
        # if self.path:
        #     cookie += ";path=%s" % self.path
        # if self.domain:
        #     cookie += ";domain=%s" % self.domain
        if self.maxage:
            cookie += ";max-age=%s" % self.maxage
        if self.secure:
            cookie += ";secure"
        return  cookie 

# class CI_Cookie:
#     """docstring for CI_Cookie"""
#     def __init__(self,**kw):
#         self.app = kw.get('app')
#         self.data = {}


#     def parse_cookie(self,env):
#         try:
#             gid = gevent.getcurrent()
#             self.data[gid] = {}
            
#             Cookie = env.get('HTTP_COOKIE',None)
#             #print "===============\n".join(["key:%s\nvalue:%s\n" % (key,env[key]) for key in env.keys() ])
#             if Cookie == None:
#                 return
#             list_zp = [kv.split("=") for kv in  Cookie.split(";")]
#             for zp in list_zp:
#                 cod = CookieData()
#                 cod.name = zp[0].strip()
#                 cod.value = zp[1]
#                 cod.domain = ""
#                 cod.isPre = True
#                 self.data[gid][cod.name] = cod
#         except BaseException as e:
#             self.app.logger.error("%s:%s" % ( PushTraceback(),e ))

#     def __getitem__(self,key):
#         return self.get(key)

#     def __setitem__(self,key,value):
#         self.set(key,value)


#     def get(self,key):
#         gid = gevent.getcurrent()

#         v = self.data[gid].get(key,None)
#         if v == None:
#             return None
#         return v.value
        

#     def set(self,key,value,maxage=86400):
#         gid = gevent.getcurrent()
#         v = self.data[gid].get(key,None)
#         if None ==  v:
#             v = CookieData()
#             v.name = key
#         v.value = value
#         v.maxage = maxage
#         v.isPre = False
#         self.data[gid][key] = v

#     def result_cookie(self):
#         gid = gevent.getcurrent()
#         headers = [("Set-Cookie","%s" % cookiedata) for cookiedata in  self.data[gid].values() if "%s" % cookiedata <> ""]
#         self.data.pop(gid,None)
#         return headers

class CI_Cookie:
    """docstring for CI_Cookie"""
    def __init__(self,**kw):
        self.app = kw.get('app')
        self.data = local()

    def parse_cookie(self,env):
        try:
            self.data.cookie = {}
            self.cookie = self.data.cookie
            Cookie = env.get('HTTP_COOKIE',None)
            #print "===============\n".join(["key:%s\nvalue:%s\n" % (key,env[key]) for key in env.keys() ])
            if Cookie == None:
                return
            list_zp = [kv.split("=") for kv in  Cookie.split(";")]
            for zp in list_zp:
                cod = CookieData()
                cod.name = zp[0].strip()
                cod.value = zp[1]
                cod.domain = ""
                cod.isPre = True
                self.cookie[cod.name] = cod
        except BaseException as e:
            self.app.logger.error("%s:%s" % ( PushTraceback(),e ))

    def __getitem__(self,key):
        return self.get(key)

    def __setitem__(self,key,value):
        self.set(key,value)


    def get(self,key):
        v = self.cookie.get(key,None)
        if v == None:
            return None
        return v.value
        

    def set(self,key,value,maxage=86400):
        v = self.cookie.get(key,None)
        if None ==  v:
            v = CookieData()
            v.name = key
        v.value = value
        v.maxage = maxage
        v.isPre = False
        self.cookie[key] = v

    def result_cookie(self):
        return [("Set-Cookie","%s" % cookiedata) for cookiedata in  self.cookie.values() if "%s" % cookiedata <> ""]



        