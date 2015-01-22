#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import json



class CI_Router(object):
    def __init__(self,**kwargs):
        pass


    def wsgi_route(self,app,env):

        # return "hello wold"
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


        return eval('app.loader.ctrl(ctrl).'+func+'(**data)')









if __name__=='__main__':
    r=CI_Router()


