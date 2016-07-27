#!/usr/bin/env python
# -*- coding:utf8 -*-



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
        if self.path:
            cookie += ";path=%s" % self.path
        # if self.domain:
        #     cookie += ";domain=%s" % self.domain
        if self.maxage:
            cookie += ";max-age=%s" % self.maxage
        if self.secure:
            cookie += ";secure"
        return  cookie


class CI_Cookie:
    """docstring for CI_Cookie"""
    def __init__(self,**kw):
        self.app = kw.get('app')


    def parse_cookie(self,env):
        try:
            Cookie = env.get('HTTP_COOKIE',None)
            if Cookie == None:
                return
            list_zp = [kv.split("=") for kv in  Cookie.split(";")]
            for zp in list_zp:
                cod = CookieData()
                cod.name = zp[0].strip()
                cod.value = zp[1]
                cod.path  = "/"
                cod.domain = ""
                cod.isPre = True
                self.app.local.response.cookies[cod.name] = cod
        except BaseException as e:
            self.app.logger.error(e)
            # self.app.logger.error("%s:%s" % ( PushTraceback(),e ))

    def __getitem__(self,key):
        return self.get(key)

    def __setitem__(self,key,value):
        self.set(key,value)


    def get(self,key):
        v = self.app.local.response.cookies.get(key,None)
        if v == None:
            return None
        return v.value


    def set(self,key,value,maxage=86400):
        v = self.app.local.response.cookies.get(key,None)
        if None ==  v:
            v = CookieData()
            v.name = key
        v.value = value
        v.maxage = maxage
        v.isPre = False
        self.app.local.response.cookies[key] = v

    def result_cookie(self):
        [self.app.set_header("Set-Cookie","%s" % cookiedata) for cookiedata in  self.app.local.response.cookies.values() if "%s" % cookiedata != ""]




