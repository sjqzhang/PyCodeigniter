#!/usr/bin/env python
# -*- coding:utf8 -*-
r'''



## how to use?

# first way (just for test)

from codeigniter.system.core.CI_Application import CI_Application

def main():
    app=CI_Application(r'./')

    app.start_server()

if __name__ == '__main__':
    main()



## second way (recommend)


#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import web

from codeigniter.system.core.CI_Application import CI_Application


ci=CI_Application(application_path=r'./')


urls = (
    '/.*', ci.router.webpy_route
)
app = web.application(urls, globals())

session = web.session.Session(app, web.session.DiskStore('sessions'))


if __name__ == "__main__":


    app.run()



## if you want to know more,you can see models ,controllers


##controller


class Index:

    def __init__(self,abc=0, *args, **kwargs):
        self.model= kwargs['app'].loader.model('IndexModel')

    def index(self):
        return "hello world"

    def search(self):
        return  self.model.search()

    def insert(self):
       return  self.model.insert()

    def update(self):
        return  self.model.update()

    def delete(self):
        return  self.model.delete()

    def ar(self):
        return self.model.ar()

    def tran(self):
        return self.model.tran()


## model


class IndexModel(object):
    def __init__(self,**xx):
        pass

    def index(self):
        return "hello world"

    def search(self):
        return  self.app.db.query( 'select * from test')

    def insert(self):
        return self.app.db.insert('test',{'id':"123",'msg':"test"})

    def update(self):
        return self.app.db.update('test',{'msg':"tessdfasdft"},{'id':'123'})

    def delete(self):
        return self.app.db.app.db.delete('test',{'id':'123'})

    def ar(self):
        return self.app.db.ar().select("*").from_('test').limit(2).get()

    def tran(self):
        conn=self.app.db.get_connection()
        self.app.db.begin(conn)
        self.app.db.insert('test',{'id':"12398",'msg':"test"},conn)
        self.app.db.rollback(conn)
        # self.app.db.commit(conn)
        self.app.db.close(conn)







'''

__author__ = 'xiaozhang'


__all__=['system','application']

try:
    from system.core.CI_Application import CI
    from system.core.CI_Application import CI as ci
    from system.core.CI_Application import CI_Application
    from system.core.CI_Application import CI_Application as ci_application
    from system.core.CI_Application import CI_Application as applicaton
    from system.core.CI_Cache import CI_Cache
    from system.core.CI_Cache import CI_Cache as ci_cache
    from system.core.CI_Cache import CI_Cache as cache
except:
    from codeigniter.system.core.CI_Application import CI
    from codeigniter.system.core.CI_Application import CI as ci
    from codeigniter.system.core.CI_Application import CI_Application
    from codeigniter.system.core.CI_Application import CI_Application as ci_application
    from codeigniter.system.core.CI_Application import CI_Application as applicaton
    from codeigniter.system.core.CI_Cache import CI_Cache
    from codeigniter.system.core.CI_Cache import CI_Cache as ci_cache
    from codeigniter.system.core.CI_Cache import CI_Cache as cache
