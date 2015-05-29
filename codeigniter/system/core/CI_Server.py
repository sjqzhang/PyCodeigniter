#!/usr/bin/python
#-*- coding:utf-8 -*-




from reactor.fastpy import WrapFastPyServer


class CI_Server(object):

    def __init__(self,**kwargs):
        self.app=kwargs['app']
        self.server=WrapFastPyServer(**kwargs)
    def start(self):
        self.server.start()










