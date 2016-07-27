#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'



import logging
from logging.handlers import RotatingFileHandler
import traceback
import re

import sys
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class CI_Logger(object):
    def __init__(self,**kwargs):
        self.log_file_path=kwargs['file']
        self.log_level=kwargs['level']
        if 'file_size' in kwargs.keys() :
            self.file_size=kwargs['file_size']
        else:
            self.file_size=100 * 1024 * 1024
        if 'back_count' in kwargs.keys():
            self.back_count=kwargs['back_count']
        else:
            self.back_count=10

        if 'name' in kwargs.keys():
            self.name=kwargs['name']
        else:
            self.name='default'
        # self.log_formatter='%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s'
        self.log_formatter='%(asctime)s %(levelname)s %(message)s'
        self.init(self.name)
        self.loggers={}
        self.log_pattern=re.compile(r'(\w+\.py)",\s*line\s*(\d+)\,\s*in\s\<?(\w+)\>?',re.IGNORECASE)

    def init(self,name):
        if name!=None:
            self.logger=logging.getLogger(name)
        else:
            self.logger=logging.getLogger('default')
        self.set_handlers(self.log_file_path)

    def _init(self,name):
        if not name in self.loggers.keys():
            logger=logging.getLogger(name)
            self.set_handlers(self.log_file_path)
            self.loggers[name]=logger
            return logger
        else:
            return self.loggers[name]

    def _get_logger(self,loginfo):
           info=self._get_msg( loginfo)
           if len(info)>0:
                return self._init(info[0][0])
           else:
               return self.logger








    def set_handlers(self, log_file_path):
        handler = RotatingFileHandler(filename=log_file_path, maxBytes=self.file_size, backupCount=self.back_count)
        self.logger.setLevel(self.log_level)
        formatter = logging.Formatter(self.log_formatter)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self._no_handlers = False

    def _get_msg(self,loginfo):
        return self.log_pattern.findall(loginfo)


    def _get_log_back(self):
        list=traceback.format_stack()
        list.pop()
        list.pop()
        list.pop()
        return list.pop()

    def _log(self,message,level=logging.INFO):
        if level==logging.ERROR:
            ex_type, value, tb = sys.exc_info()
            errorlist = [line.lstrip() for line in traceback.format_exception(ex_type, value, tb)]
            # errorlist=traceback.format_exception()
            # errorlist.pop()
            # errorlist.pop()
            # errorlist.pop()
            # print(type(errorlist))
            errorlist.reverse()
            self.logger.log(level,"".join(errorlist))
        else:
            loginfo=self._get_log_back()
            if PY2:
                if isinstance(message,unicode):
                    message=unicode.encode(message,'utf-8','ignore')
                message = str( self._get_msg( loginfo)[0])+" "+str(message)
                self.logger.log(level,message)
            if PY3:
                message = str( self._get_msg( loginfo)[0])+" "+str(message)
                self.logger.log(level,message)

    # def log(self,message,level=logging.INFO):
    #     loginfo=self._get_log_back()
    #     message = str( self._get_msg( loginfo)[0])+" "+str(message)
    #     self.logger.log(level,message)

    def info(self,message):
        if logging.INFO>=self.log_level:
            self._log(message,logging.INFO)

    def error(self,message):
        if logging.ERROR>=self.log_level:
            self._log(message,logging.ERROR)

    def warn(self,message):
        if logging.WARN>=self.log_level:
            self._log(message,logging.WARN)

    def debug(self,message):
        if logging.DEBUG>=self.log_level:
            self._log(message,logging.DEBUG)








if __name__=='__main__':
    logger=CI_Logger(log_file="e:/log/abc.log",log_level=logging.INFO)
    logger.log("sdfasdfasdf")


