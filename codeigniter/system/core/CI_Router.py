#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import json

from urlparse import parse_qs



class CI_Router(object):
    def __init__(self,**kwargs):
        pass

    def parse_data(self,env):
        if env.has_key('REQUEST_METHOD') and env['REQUEST_METHOD']=='POST':
            try:
                request_body_size = int(env.get('CONTENT_LENGTH', 0))
                request_body = env['wsgi.input'].read(request_body_size)
                d = parse_qs(request_body)
                env['__FORM__DATA__']=d
            except (ValueError):
                request_body_size = 0



    def wsgi_route(self,app,env):
        env['__FORM__DATA__']={}

        self.parse_data(env);






        query=env['QUERY_STRING']
        path=env['PATH_INFO']
        paths=path[1:].split(r'/')
        if len(paths)>=2:
            func= paths[ len(paths)-1]
            ctrl= paths[ len(paths)-2]
        elif len(paths)==1:
            ctrl='Index'
            func=paths[0]
        else:
            ctrl='Index'
            func='index'

        items=query.split(r'&')
        data={}
        for i in items:
            item=i.split(r'=')
            if len(item)==2:
                data[item[0]]=item[1]
            elif len(item)==1 and item[0]!='':
                data[item[0]]=''

        data=dict( data.items()+env['__FORM__DATA__'].items())

        try:
            for k in data.keys():
                if k.find('[]')!=-1:
                    if isinstance(data[k],list):
                        data[k]= eval(data[k][0])
                elif isinstance(data[k],list):
                    data[k]=unicode( data[k][0],'utf-8')
        except UnicodeDecodeError as e:
            app.logger.warn(str(e)+str(data))
        except Exception as e:
            app.logger.error(e)


        try:
            ctrl_instance=app.loader.ctrl(ctrl)
            if not hasattr(ctrl_instance,func):
                 return "Not Found"
        except Exception as err:
            return "Not Found"
        try:
            return eval('app.loader.ctrl(ctrl).'+func+'(**data)')
        except Exception as e:
            app.logger.error('when call controller %s function %s error,%s'%(ctrl,func,str(e)))









if __name__=='__main__':
    r=CI_Router()


