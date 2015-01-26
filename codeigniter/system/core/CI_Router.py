#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import json





class CI_Router(object):
    def __init__(self,**kwargs):
        self.app=kwargs['app']

    def wsgi_route(self,env):

        data=self.app.input.parse(env)
        try:
            if data.has_key('__ctrl_name__'):
                ctrl=data['__ctrl_name__']
                del data['__ctrl_name__']

            if data.has_key('__func_name__'):
                func=data['__func_name__']
                del data['__func_name__']
            ctrl_instance=self.app.loader.ctrl(ctrl)
            if not hasattr(ctrl_instance,func):
                 return "Not Found"
        except Exception as err:
            return "Not Found"
        try:
            return eval('app.loader.ctrl(ctrl).'+func+'(**data)')
        except Exception as e:
            self.app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))


    def webpy_route(self):
        import web
        return self.wsgi_route(web.ctx['environ'])






if __name__=='__main__':
    r=CI_Router()


