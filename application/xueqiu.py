#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'





import os
import sys

import gevent

from gevent import monkey

monkey.patch_socket()

from wsgiref.simple_server import make_server

import web

import apscheduler


def app_run(system_path,application_path):
    sys.path.insert(0,application_path)
    sys.path.insert(0,system_path+os.path.sep+'core')
    exec(r'from CI_Application import CI_Application')
    app=CI_Application(system_path,application_path)
    return app

def request_hander(*args,**kwargs):

    print(args)
    print(kwargs)
    print "hello world"

def start_server(app):

    httpd=make_server(app.config['server']['host'],app.config['server']['port'],app.request_hander)
    httpd.serve_forever()


def start_gevent_server(app):
    from gevent.pool import Pool
    from gevent.wsgi import WSGIServer
    from gevent import monkey
    monkey.patch_all()
    pool = Pool(10000) # do not accept more than 10000 connections
    server = WSGIServer(('0.0.0.0', 1234), app.request_hander, spawn=pool)
    server.serve_forever()



def start_fetch(app):
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler({

        'apscheduler.executors.default': {
            'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
            'max_workers': '20'
        },
        'apscheduler.executors.processpool': {
            'type': 'processpool',
            'max_workers': '5'
        },
        'apscheduler.job_defaults.coalesce': 'false',
        'apscheduler.job_defaults.max_instances': '3',
        'apscheduler.timezone': 'UTC',
    })

    # app.loader.ctrl('XueQiu').load_news_urls()
    # app.loader.ctrl('XueQiu').load_json_url()
    scheduler.add_job(app.loader.ctrl('XueQiu').load_news_urls, 'interval', minutes=1)
    scheduler.add_job(app.loader.ctrl('XueQiu').load_url, 'interval', minutes=1)
    scheduler.start()




if __name__=='__main__':
    import  platform
    if platform.system()=='Windows':
        app=app_run(r'E:\python\study\PyCodeigniter\system',r'E:\python\study\PyCodeigniter\application')
    else:
        app=app_run(r'/var/www/pyexample/PyCodeigniter/system',r'/var/www/pyexample/PyCodeigniter/application')




    # app.loader.ctrl('XueQiu').load_url()
    # app.loader.ctrl('XueQiu').load_news_urls()
    # app.loader.ctrl('XueQiu').load_json_url()


    start_fetch(app)



    # app.mail.send('s-jqzhang@meizu.com',"测试一下",urllib2.urlopen("http://news.163.com").read())



    # app.logger.warn('xxxxxxxxxx')


    # test(app)

    # start_server(app)


    # start_gevent_server(app)



