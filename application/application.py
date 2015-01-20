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


def test(app):
    app.loader.model('IndexModel').search()
    print app.loader.ctrl('Index').add(3,4)
    import time
    start=time.time()
    def job():


        count=100
        while count>0:
            app.loader.model('IndexModel').search()
            # print("hellow")
            count=count-1


    import gevent
    from gevent import monkey

    monkey.patch_socket()
    jobs=[]
    for i in xrange(0,10):
        jobs.append(gevent.spawn(job))
        # job()

    gevent.joinall(jobs)



    print(time.time()-start)


    # job()

    # app.db.query("insert into test(id,msg) values({id},{msg})",{'id':6,'msg':"asdfasdf"})


    # app.db.insert('test',{'id':'6','msg':"asdfa'sdf"})



    db=app.loader.cls('CI_DBActiveRec')(**app.config['db'])

    print(db)


    print db.query('select * from test')



if __name__=='__main__':
    import  platform
    if platform.system()=='Windows':
        app=app_run(r'E:\python\study\PyCodeigniter\system',r'E:\python\study\PyCodeigniter\application')
    else:
        app=app_run(r'/var/www/pyexample/PyCodeigniter/system',r'/var/www/pyexample/PyCodeigniter/application')








    # app.mail.send('s-jqzhang@meizu.com',"测试一下",urllib2.urlopen("http://news.163.com").read())



    # app.logger.warn('xxxxxxxxxx')


    # test(app)

    start_server(app)


    # start_gevent_server(app)



