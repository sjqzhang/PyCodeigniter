#!/usr/bin/python
#-*- coding:utf-8 -*-






class CI_Server(object):

    def __init__(self,**kwargs):
        import sys
        # print sys.path
        self.app=kwargs['app']
        from reactor.fastpy import WrapFastPyServer
        self.server=WrapFastPyServer(**kwargs)
        self.pre_route_callback=None
        self.post_route_callback=None
    def start(self):
        self.server.start()

    def pre_route(self,callback):
        self.pre_route_callback=callback

    def post_route(self,callback):
        self.post_route_callback=callback










