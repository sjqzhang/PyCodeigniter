#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import sys
import os
import json
import imp



CI={'app':None}


def get_application():
    if 'app' in CI.keys():
        return CI['app']
    else:
        return None

class CI_Application(object):
    application_instance=None
    def __init__(self,application_path=None,system_path=None,config_file=None):
        if system_path==None:
            system_path=os.path.dirname( os.path.dirname(__file__))
        self.system_path=system_path
        self.application_path=application_path
        self.config_file=config_file
        self.config={}
        self.loader=None
        self.logger=None
        self.db=None
        self.cache=None
        self.cron=None
        self.server=None
        self._app_create(application_path)
        CI['app']=self
        self.init()






    @staticmethod
    def get_application():
        if 'app' in CI.keys():
            return CI['app']
        else:
            return None
    def init(self):
        if self.config_file!=None:
            PY2 = sys.version_info[0] == 2
            if PY2:
                execfile(self.config_file,{},self.config)
            else:
                exec(compile(open(self.config_file).read(), self.config_file, 'exec'))
        else:
            sys.path.insert(0,self.application_path+os.path.sep+'config')
            config=__import__('config')
            self.config=config.config
        sys.path.insert(0,self.system_path+os.path.sep+'core')
        sys.path.insert(0,self.system_path+os.path.sep+'core'+ os.path.sep+ 'reactor')
        # sys.path.insert(0,self.application_path+os.path.sep+'config')
        # config=__import__('config')
        # self.config=config.config
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
        module_list=['CI_Logger','CI_Loader','CI_Mail','CI_Router','CI_DB','CI_DBActiveRec','CI_Input','CI_Cache','CI_Cron']
        for m in module_list:
            exec('from '+ m +' import '+m)
        self.logger= eval('CI_Logger(**self.config["log"])')

        self.input= eval('CI_Input(**self.config)')
        if 'db' in self.config.keys():
            self.db= eval('CI_DB(**self.config["db"])')
        else:
            self.logger.warn('db not config')
        self.loader= eval('CI_Loader(**self.config)')
        self.router= eval('CI_Router(**self.config)')
        if 'mail' in self.config.keys():
            self.mail= eval('CI_Mail(**self.config["mail"])')
        if 'cache' in self.config.keys():
            self.cache= eval('CI_Cache(**self.config)')
        if 'cron' in self.config.keys():
            self.cron= eval('CI_Cron(**self.config)')
        if 'server' in self.config.keys():
            exec('from CI_Server import CI_Server')
            # print self.loader.load_file('CI_Server')
            self.server= eval('CI_Server(**self.config)')
        sys.path.remove(self.system_path+os.path.sep+'core')
        if self.config_file==None:
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
                pass
                # os.unlink(initfile)

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
        html=''
        code,obj=self.router.wsgi_route(environ)
        if not isinstance(obj,str):
            html=json.dumps(obj)
            start_response(str(code), [('Content-Type', 'application/json')])
        else:
            start_response(str(code), [('Content-Type', 'text/html')])
            html=obj
        return [str(html)]


    def start_server(self):
        from wsgiref.simple_server import make_server
        httpd=make_server(self.config['server']['host'],self.config['server']['port'],self.request_hander)
        msg="server listen to : "+str(self.config['server']['port'])
        self.logger.info(msg)
        print(msg)
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






