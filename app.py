#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



import os
import sys
from wsgiref.simple_server import make_server

def app_run(system_path,application_path):
    sys.path.insert(0,application_path)
    sys.path.insert(0,system_path+os.path.sep+'core')
    exec(r'from CI_Application import CI_Application')
    app=CI_Application(system_path,application_path)
    return app


def start_server(app):
    httpd=make_server(app.config['server']['host'],app.config['server']['port'],app.request_hander)
    httpd.serve_forever()

if __name__=='__main__':
    app=app_run('./system','./application')
    start_server(app)


