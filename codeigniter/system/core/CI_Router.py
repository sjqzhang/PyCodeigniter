#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import json
import re
import time
import logging
from logging.handlers import RotatingFileHandler
import datetime
import inspect

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import cgi

try:
    import web,cgi,os
except Exception as e:
    pass
from CI_Application import CI

from CI_Request import CI_Request

class CI_Router(object):
    def __init__(self,**kwargs):
        self.app=kwargs['app']
        self.config=self.app.config
        self.access_log=logging.getLogger('access_log')
        self.error_log=logging.getLogger('error_log')
        self.access_log.setLevel(logging.DEBUG)
        self.error_log.setLevel(logging.WARN)
        if 'access_log' in self.config['server']:
            self.access_log_file= self.config['server']['access_log']
        else:
            self.access_log_file='./access.log'
        if 'error_log' in self.config['server']:
            self.error_log_file= self.config['server']['error_log']
        else:
            self.error_log_file='./error.log'
        self._methods={}

        error_log={

            'file':self.error_log_file,
            'level':logging.WARN,
            'file_size':1024*1024*100,
            'back_count':10

        }

        acchandler = RotatingFileHandler(filename=self.access_log_file, maxBytes=1024*1024*1024, backupCount=10)
        # errhandler = RotatingFileHandler(filename=self.error_log_file, maxBytes=1024*1024*1024, backupCount=10)
        # format='%(asctime)s %(message)s'
        # acchandler.setFormatter(format)
        # errhandler.setFormatter(format)
        self.access_log.addHandler(acchandler)

        exec('from CI_Logger import CI_Logger')
        self.error_log= eval('CI_Logger(**error_log)')

        # self.error_log.addHandler(errhandler)


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

            return '200 OK',eval('self.app.loader.ctrl(ctrl).'+func+'("","")')
        except TypeError as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))
            return '200 OK',{'message':str(e),'code':500}
        except Exception as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))
            return  "500 Internal server error","Server Error,Please see log file"



    def _log(self,env,code,stime):
        etime=time.time()
        etime=etime-stime
        etime="%0.6f" % etime
        now = datetime.datetime.now()
        dt=now.strftime('%Y-%m-%d %H:%M:%S')
        method=env['REQUEST_METHOD']
        try:
            for i in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'REMOTE_ADDR']:
                if i in env.keys():
                    addr=str(env[i]).strip()
                    break
        except Exception as er:
            addr=env['REMOTE_ADDR']
        path=env['PATH_INFO']
        protol=env['SERVER_PROTOCOL']
        message="%s - - [%s] \"%s %s %s\" %s %s" % (addr,dt,method,path,protol,str(code),etime)
        self.access_log.info(message)

    def wsgi_route(self,env):
        # print(env)
        stime=time.time()
        data=self.app.input.parse(env)
        try:
            try:
                if False == self.app.hook.call_pre_controller(env):
                    if self.app.local.response.body == "":
                        self.app.set500("pre_controller hook result false")
                    return
                if 'session' in self.config.keys():
                    self.app.session.pre_parse_uuid()
                if '__ctrl_name__' in data.keys():
                    controller_name=data['__ctrl_name__']
                    del data['__ctrl_name__']
                if '__func_name__' in data.keys():
                    func=data['__func_name__']
                    del data['__func_name__']
                if self.app.static:
                    if self.app.static.accept(env):
                        return self.app.static.route(env)
                for i in range(1):
                    if 'route' in self.config.keys():
                        for route,ctrl in self.config['route'].iteritems():
                            if re.match(route,env['PATH_INFO']) or route.strip() == env['PATH_INFO'].strip():
                                ctrl,func  = ctrl.split(".")
                                ctrl_instance=self.app.loader.ctrl(ctrl)
                                if not hasattr(ctrl_instance,func) or str(func).startswith('_'):
                                    self.app.set404()
                                    return
                                break
                    ctrl_instance=self.app.loader.ctrl(controller_name)
                    f=self.get_func(ctrl_instance,func)
                    if f!=None:
                        func=f
                    if not hasattr(ctrl_instance,func) or str(func).startswith('_'):
                        self.app.set404()
                        return
            except Exception as err:
                self._log(env,404,stime)
                self.app.set404()
                return
            try:
                if False == self.app.hook.call_post_controller_constructor(env,ctrl_instance,func):
                    if self.app.local.response.body == "":
                        self.app.set500("post_controller_constructor hook result false")
                    return
                ret= getattr(ctrl_instance,func)(**data)
                self._log(env,200,stime)
                self.app.set200(ret)
                self.app.hook.call_post_controller(env,ctrl_instance,func,ret)
                return 
            except TypeError as e:
                self.error_log.error(e)
                self.app.logger.error('when call controller %s function %s error,%s'%(controller_name,func,str(e)))
                self._log(env,500,stime)
                self.app.set200({'message':str(e),'code':500})
                return
            except Exception as e:
                self.error_log.error(e)
                self._log(env,500,stime)
                self.app.logger.error('when call controller %s function %s error,%s'%(controller_name,func,str(e)))
                self.app.set500("Server Error,Please see log file")
                return
        finally:
            if 'session' in self.config.keys():
                self.app.session.release()
            


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


    def input(self,app,env):
        if env['REQUEST_METHOD'] in ['POST', 'PUT']:
            if env.get('CONTENT_TYPE', '').lower().startswith('multipart/'):
                fp = env['wsgi.input']
                a = cgi.FieldStorage(fp=fp, environ=env, keep_blank_values=1)
            else:
                fp = StringIO(env.get('wsgi.input').read())
                a = cgi.FieldStorage(fp=fp, environ=env, keep_blank_values=1)
        else:
            a = cgi.FieldStorage(environ=env, keep_blank_values=1)
        app.local.input={}
        for key in a.keys():
            app.local.input[ key ] = a[key].value
        return app.local.input

    def wsgi(self,env):
        stime=time.time()
        path=env['PATH_INFO'].split('/')
        if PY2:
            path=filter(lambda p:p!='',path)
        if PY3:
            path=list(filter(lambda p:p!='',path))
        controller_name=''

        req=CI_Request(env)

        if len(path)>=2:
            controller_name=path[0]
            func=path[1]
        elif len(path)==1:
            controller_name='index'
            func=path[0]
        # data=self.input(self.app,env)
        try:
            try:
                if False == self.app.hook.call_pre_controller(env):
                    if self.app.local.response.body == "":
                        self.app.set500("pre_controller hook result false")
                    return
                if 'session' in self.config.keys():
                    self.app.session.pre_parse_uuid()
                # if '__ctrl_name__' in data.keys():
                #     controller_name=data['__ctrl_name__']
                #     del data['__ctrl_name__']
                # if '__func_name__' in data.keys():
                #     func=data['__func_name__']
                #     del data['__func_name__']
                if self.app.static:
                    if self.app.static.accept(env):
                        self.app.local.response.status,self.app.local.response.body= self.app.static.route(env)
                        return
                for i in range(1):
                    if 'route' in self.config.keys():
                        for route,ctrl in self.config['route'].iteritems():
                            if re.match(route,env['PATH_INFO']) or route.strip() == env['PATH_INFO'].strip():
                                ctrl,func  = ctrl.split(".")
                                ctrl_instance=self.app.loader.ctrl(ctrl)
                                if not hasattr(ctrl_instance,func) or str(func).startswith('_'):
                                    self.app.set404()
                                    return
                                break
                    ctrl_instance=self.app.loader.ctrl(controller_name)
                    f=self.get_func(ctrl_instance,func)
                    if f!=None:
                        func=f
                    if not hasattr(ctrl_instance,func) or str(func).startswith('_'):
                        self.app.set404()
                        return
            except Exception as err:
                self.error_log.error(err)
                self._log(env,404,stime)
                self.app.set404()
                return
            try:
                if False == self.app.hook.call_post_controller_constructor(env,ctrl_instance,func):
                    if self.app.local.response.body == "":
                        self.app.set500("post_controller_constructor hook result false")
                    return
                funcobj = getattr(ctrl_instance,func)
                if not callable(funcobj):
                    self.app.set404()
                    return
                ret= getattr(ctrl_instance,func)(req,self.app.local.response)
                if self.app.local.response.body=="":
                    self.app.local.response.body=ret
                self._log(env,200,stime)
                # self.app.set200(ret)
                self.app.hook.call_post_controller(env,ctrl_instance,func,ret)
                return
            except TypeError as e:
                self.error_log.error(e)
                self.app.logger.error('when call controller %s function %s error,%s'%(controller_name,func,str(e)))
                self._log(env,500,stime)
                self.app.set200({'message':str(e),'code':500})
                return
            except Exception as e:
                self.error_log.error(e)
                self._log(env,500,stime)
                self.app.logger.error('when call controller %s function %s error,%s'%(controller_name,func,str(e)))
                self.app.set500("Server Error,Please see log file")
                return
        finally:
            if 'session' in self.config.keys():
                self.app.session.release()












if __name__=='__main__':
    r=CI_Router()


