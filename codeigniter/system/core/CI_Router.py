#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import json
import re
import time
import logging
from logging.handlers import RotatingFileHandler
import datetime

try:
    import web,cgi,os
except Exception as e:
    pass







class CI_Router(object):
    def __init__(self,**kwargs):
        self.app=kwargs['app']
        self.config=self.app.config
        self.access_log=logging.getLogger('access_log')
        self.error_log=logging.getLogger('error_log')
        self.access_log.setLevel(logging.DEBUG)
        self.error_log.setLevel(logging.DEBUG)
        if 'access_log' in self.config['server']:
            self.access_log_file= self.config['server']['access_log']
        else:
            self.access_log_file='./access.log'
        if 'error_log' in self.config['server']:
            self.error_log_file= self.config['server']['error_log']
        else:
            self.error_log_file='./error.log'
        self._methods={}
        acchandler = RotatingFileHandler(filename=self.access_log_file, maxBytes=1024*1024*1024, backupCount=10)
        errhandler = RotatingFileHandler(filename=self.access_log_file, maxBytes=1024*1024*1024, backupCount=10)
        format='%(asctime)s %(message)s'
        acchandler.setFormatter(format)
        errhandler.setFormatter(format)
        self.access_log.addHandler(acchandler)
        self.error_log.addHandler(errhandler)


    def get_func(self,ctrl,func):
        funclist=dir(ctrl)
        for f in funclist:
            if(f.startswith('_')):
                continue
            else:
                if f.lower()==func.lower():
                    return f
        return None


    def route(self,ctrl,func,data={},request=None):
        try:
            ctrl_instance=self.app.loader.ctrl(ctrl)
            f=self.get_func(ctrl_instance,func)
            if f!=None:
                func=f
            if not hasattr(ctrl_instance,func) or str(func).startswith('_'):
                 return "404 Not Found", "Not Found"

            # if request!=None:
                # if 'req' not in data.keys():
                #     data['req']=request
                # else:
                #     data['__request__']=request

            return '200 OK',eval('self.app.loader.ctrl(ctrl).'+func+'(**data)')
        except TypeError as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))
            return '200 OK',{'message':str(e),'code':500}
        except Exception as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))
            return  "500 Internal server error","Server Error,Please see log file"



    def _log(self,env,code,etime):
        now = datetime.datetime.now()
        dt=now.strftime('%Y-%m-%d %H:%M:%S')
        method=env['REQUEST_METHOD']
        addr=env['REMOTE_ADDR']
        path=env['PATH_INFO']
        protol=env['SERVER_PROTOCOL']
        message="'%s - - [%s] %s %s %s %s %s'" % (addr,dt,method,path,protol,str(code),etime)
        self.access_log.info(message)



    def wsgi_route(self,env):
        stime=time.time()
        data=self.app.input.parse(env)
        try:
            if '__ctrl_name__' in data.keys():
                ctrl=data['__ctrl_name__']
                del data['__ctrl_name__']

            if '__func_name__' in data.keys():
                func=data['__func_name__']
                del data['__func_name__']
            ctrl_instance=self.app.loader.ctrl(ctrl)
            #print(dir(ctrl_instance))
            f=self.get_func(ctrl_instance,func)
            if f!=None:
                func=f
            if not hasattr(ctrl_instance,func) or str(func).startswith('_'):
                 return "404 Not Found", "Not Found"
        except Exception as err:
            return "404 Not Found", "Not Found"
        try:
            ret=eval('self.app.loader.ctrl(ctrl).'+func+'(**data)')
            etime=time.time()
            self._log(env,etime-stime)
            return '200 OK',ret
        except TypeError as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))
            return '200 OK',{'message':str(e),'code':500}
        except Exception as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))
            return  "500 Internal server error","Server Error,Please see log file"


    def webpy_route(self):
        try:
            code,obj= self.wsgi_route(web.ctx['environ'])
            if isinstance(obj,str):
                return obj
            else:
                return str(json.dumps(obj))
        except Exception as e:
            self.app.logger.error(e)
            return "Server Error"







if __name__=='__main__':
    r=CI_Router()


