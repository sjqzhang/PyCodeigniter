#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import sys
import os

from wsgiref.simple_server import make_server


class CI_Application(object):
    def __init__(self,application_path=None,system_path=None):
        if system_path==None:
            system_path=os.path.dirname( os.path.dirname(__file__))
        self.system_path=system_path
        self.application_path=application_path
        self.config={}
        self.loader=None
        self.logger=None
        self.db=None
        self._app_create(application_path)
        self.init()

    def _default_config(self):
        config='''
import logging


db={
    'host':'172.16.132.230',
    'user':'root',
    'passwd':'root',
    'database':'test',
    'maxconnections':3,
    'blocking':True,
}

log={

    'log_file':r'/log/abc.log',
    'log_level':logging.INFO

}

config={

'log':log,
'db':db

}


if __name__=='__main__':
    print(config)

        '''

        return config


    def init(self):
        sys.path.insert(0,self.system_path+os.path.sep+'core')
        sys.path.insert(0,self.application_path+os.path.sep+'config')
        config=__import__('config')
        self.config=config.config
        self.config['system_path']=self.system_path
        self.config['application_path']=self.application_path
        self.config['app']=self
        for conf in self.config.keys():
            if isinstance(self.config[conf],dict):
                self.config[conf]['app']=self
        # exec('from CI_Loader import CI_Loader')
        # exec('from CI_Logger import CI_Logger')
        # exec('from CI_DB import CI_DB')
        # exec('from CI_DBActiveRec import CI_DBActiveRec')
        # exec('from CI_Router import CI_Router')
        # exec('from CI_Mail import CI_Mail')
        module_list=['CI_Logger','CI_Loader','CI_Mail','CI_Router','CI_DB','CI_DBActiveRec','CI_Input']
        for m in module_list:
            exec('from '+ m +' import '+m)
        self.logger= eval('CI_Logger(**self.config["log"])')
        self.loader= eval('CI_Loader(**self.config)')
        self.input= eval('CI_Input(**self.config)')
        if 'db' in self.config.keys():
            self.db= eval('CI_DBActiveRec(**self.config["db"])')
        else:
            self.logger.warn('db not config')
        self.router= eval('CI_Router(**self.config)')
        self.mail= eval('CI_Mail(**self.config["mail"])')
        sys.path.remove(self.system_path+os.path.sep+'core')
        sys.path.remove(self.application_path+os.path.sep+'config')
        for m in module_list:
            try:
                module=__import__(m)
                self.loader.regcls(m,getattr(module,m))
            except:
                try:
                    self.loader.regcls(m,eval(m))
                except:
                    pass

    def _app_create(self,application_path):
        sys_app_path=os.path.dirname( os.path.dirname( os.path.dirname(__file__)))+ os.path.sep+'application'
        for file in ['__init__.py','__init__.pyc']:
            initfile=sys_app_path+ os.path.sep+file
            if os.path.isfile(initfile):
                os.unlink(initfile)

        floder_list=['controllers','models','helpers','library','config']
        for folder in floder_list:
            folder_path=application_path+os.path.sep+folder
            if not os.path.isdir( folder_path):
                cur_path=sys_app_path+ os.path.sep+ folder
                os.mkdir(folder_path)
                for file in os.listdir(cur_path):
                    target_file= os.path.join(folder_path,  file)
                    if not os.path.isfile(target_file):
                        open(target_file,"wb").write(open(os.path.join(cur_path,file),"rb").read())



    def request_hander(self, environ, start_response):
        pass
        status = '200 OK' # HTTP Status
        headers = [('Content-type', 'text/plain')] # HTTP Headers
        start_response(status, headers)

        result= self.router.wsgi_route(self,environ)

        return list(str(result))

    def start_server(self):
        httpd=make_server(self.config['server']['host'],self.config['server']['port'],self.request_hander)
        self.logger.info("server listen to : "+str(self.config['server']['port']))
        httpd.serve_forever()




if __name__=='__main__':
    pass
    # import platform
    # if platform.system()=='Windows':
    #     # app=CI_Application(r'E:\python\study\Codeigniter\system',r'E:\python\study\Codeigniter\application')
    #     app=CI_Application(r'E:\python\study\Codeigniter\system',r'I:/python_src')
    # else:
    #     app=CI_Application(r'/var/www/pyexample/Codeigniter/system',r'/var/www/pyexample/Codeigniter/application')
    # # print(app.loader)
    #
    # app.init()
    # print app.loader.model('SearchModel')['aclass']().search()

    # app.logger.log("sdfasf")


    # app.app_create('I:/python_src')

    # print app.loader.ctrl('Hello').add(4,5)
    # print app.loader.ctrl('Hello').select()


    # app.loader.model('SearchModel').search()

   # 0 print app.logger.log(app.db.query("select * from test"))






