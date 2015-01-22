#!/usr/bin/env python
# -*- coding:utf8 -*-
r'''



## how to use?


from codeigniter.system.core.CI_Application import CI_Application

def main():
    app=CI_Application(r'./')

    app.start_server()

if __name__ == '__main__':
    main()


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

    def upate(self):
        return  self.model.upate()

    def delete(self):
        return  self.model.delete()

## model

class IndexModel(object):
    def __init__(self,**xx):
        pass

    def index(self):
        return "hello world"

    def search(self):
        return  self.app.db.mquery(self.app.db.get_connection(), 'select * from test')

    def insert(self):
        return self.app.db.insert('test',{'id':"123",'msg':"test"})

    def upate(self):
        self.app.db.update('test',{'msg':"tessdfasdft"},{'id':'123'})

    def delete(self):
        self.app.db.app.db.delete('test',{'id':'123'})


'''

__author__ = 'xiaozhang'


__all__=['system','application']


