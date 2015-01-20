#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'





import os
import sys

def app_run(system_path,application_path):
    sys.path.insert(0,application_path)
    sys.path.insert(0,system_path+os.path.sep+'core')
    exec(r'from CI_Application import CI_Application')
    app=CI_Application(system_path,application_path)
    return app


if __name__=='__main__':
    import  platform
    if platform.system()=='Windows':
        app=app_run(r'E:\python\study\PyCodeigniter\system',r'E:\python\study\PyCodeigniter\application')
    else:
        app=app_run(r'/var/www/pyexample/PyCodeigniter/system',r'/var/www/pyexample/PyCodeigniter/application')

    app.loader.model('IndexModel').search()
    print app.loader.ctrl('Index').add(3,4)




    # app.db.query("insert into test(id,msg) values({id},{msg})",{'id':6,'msg':"asdfasdf"})


    # app.db.insert('test',{'id':'6','msg':"asdfa'sdf"})



    db=app.loader.cls('CI_DBActiveRec')(**app.config['db'])

    print(db)


    print db.query('select * from test')



    # app.logger.warn('xxxxxxxxxx')




