#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

'''
CREATE TABLE `test` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `msg` VARCHAR(200) DEFAULT NULL,
  `ids` VARCHAR(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=INNODB ;
'''



class IndexModel(object):
    def __init__(self,**xx):
        pass

    #def index(self):
    #    return "hello world"

    #def search(self):
    #    print 'xxxxxx'
    #    ret=  self.app.db.query( 'select * from test')
    #    print 'xxxxxxxxxxxxxxxx'
    #    return ret

    #def insert(self):
    #    return self.app.db.insert('test',{'id':"123",'msg':"test"})

    #def update(self):
    #    return self.app.db.update('test',{'msg':"tessdfasdft"},{'id':'123'})

    #def delete(self):
    #    return self.app.db.app.db.delete('test',{'id':'123'})

    #def ar(self):
    #    return self.app.db.ar().select("*").from_('test').limit(2).get()

    #def tran(self):
    #    conn=self.app.db.get_connection()
    #    self.app.db.begin(conn)
    #    self.app.db.insert('test',{'id':"12398",'msg':"test"},conn)
    #    self.app.db.rollback(conn)
    #    # self.app.db.commit(conn)
    #    self.app.db.close(conn)




