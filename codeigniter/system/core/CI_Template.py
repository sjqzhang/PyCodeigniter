#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import logging
import os
logger=logging.getLogger()


try:
    from jinja2 import Environment, FileSystemLoader
except Exception as er:
    logger.error(er)

try:
    import tenjin
    from tenjin.helpers import *
except Exception as er:
    logger.error(er)


class CI_Template(object):
    def __init__(self,**kwargs):
        self.app=kwargs['app']
        self.config={}
        self.engine_type='jinja2'
        self.env=None
        if 'template' in self.app.config:
            self.config=self.app.config['template']
            self.engine_type=self.app.config['template']['engine']
        else:
            self.config['path']='./views'
            self.engine_type=''
        if self.engine_type=='jinja2':
            self.env = Environment(loader=FileSystemLoader(self.config['path']))
        elif self.engine_type=='Tenjin':
            self.engine = tenjin.Engine()



    def render(self,template_name,data={}):
        if self.env!=None:
            template=self.env.get_template(template_name)
            return template.render(data)
        else:
            return self.engine.render( self.config['path']+ os.path.sep+template_name,data)



