#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import json
import re


try:
    import web,cgi,os
except Exception as e:
    pass



class CI_Router(object):
    def __init__(self,**kwargs):
        self.app=kwargs['app']
        self._methods={}


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






    def wsgi_route(self,env):
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
            return '200 OK',eval('self.app.loader.ctrl(ctrl).'+func+'(**data)')
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


