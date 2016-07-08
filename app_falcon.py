#!/usr/bin/env python
# -*- coding:utf8 -*-
import falcon
import json
from codeigniter import CI_Application
ciapp=CI_Application(r'./')
from wsgiref.simple_server import make_server
def dispatch(req,resp):
    resp.status = falcon.HTTP_200
    resp.body=None
    paths=filter(lambda x: x!='',req.path.split('/'))
    ctrl_name='index'
    func_name='index'
    if len(paths)>=2:
        ctrl_name=paths[0]
        func_name=paths[1]
    elif len(paths)==1:
        func_name=paths[0]
    ctrl=ciapp.loader.ctrl(ctrl_name)
    if ctrl==None or not hasattr(ctrl,func_name):
        resp.status=falcon.HTTP_404
        resp.body="Not Found"
    else:
        try:
            content=getattr(ctrl,func_name)(req,resp)
            if  resp.body==None:
                if isinstance(content,unicode):
                    resp.body=unicode.encode(content,'utf-8','ignore')
                elif isinstance(content,str):
                    resp.body=content
                else:
                    resp.body=json.dumps(content)
        except Exception as er:
            resp.status=falcon.HTTP_500
            resp.body='Internal  Error'
            print(er)
app = falcon.API()
app.add_sink(dispatch,'/')

# make_server('0.0.0.0',8000,app).serve_forever()

