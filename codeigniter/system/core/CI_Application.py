#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import sys
import os
import json
import imp



import pdb

class CI_CLASS(object):

    def __getattr__(self,attr):
        ci = CI_Application.application_instance
        if hasattr(ci,attr):
            return getattr(ci,attr)
        return None

CI = CI_CLASS()


class CI_Application(object):
    application_instance=None
    def __init__(self,application_path=None,system_path=None,config_file=None):
        # pdb.set_trace()
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
        self.mail=None
        self.server=None
        self.tpl=None
        self.zk=None
        self._app_create(application_path)
        CI_Application.application_instance = self
        self.init()




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
        exec('from CI_Logger import CI_Logger')
        self.logger= eval('CI_Logger(**self.config["log"])')
        module_list=['CI_Loader','CI_Mail','CI_Router','CI_Input','CI_Cache']
        for m in module_list:
            try:
                exec('from '+ m +' import '+m)
            except Exception as err:
                self.logger.error(err)
        self.input= eval('CI_Input(**self.config)')

        if 'session' in self.config.keys():
            exec('from CI_Cookie import CI_Cookie')
            self.cookie= eval('CI_Cookie(**self.config)')
            module_list.append('CI_Cookie')
            
        if 'db' in self.config.keys():
            exec('from CI_DB import CI_DB')
            exec('from CI_DBActiveRec import CI_DBActiveRec')
            self.db= eval('CI_DB(**self.config["db"])')
            module_list.append('CI_DB')
            module_list.append('CI_DBActiveRec')
        else:
            self.logger.warn('db not config')
        self.router= eval('CI_Router(**self.config)')
        if 'mail' in self.config.keys():
            self.mail= eval('CI_Mail(**self.config["mail"])')
            module_list.append('CI_Mail')
        if 'cache' in self.config.keys():
            self.cache= eval('CI_Cache(**self.config)')
        if 'server' in self.config.keys() and 'fastpy' in self.config['server'] and  self.config['server']['fastpy'] :
            exec('from CI_Server import CI_Server')
            self.server= eval('CI_Server(**self.config)')
            module_list.append('CI_Server')
        self.loader= eval('CI_Loader(**self.config)')
        if 'cron' in self.config.keys():
            exec('from CI_Cron import CI_Cron')
            self.cron= eval('CI_Cron(**self.config)')
            module_list.append('CI_Cron')
        if 'zookeeper' in self.config.keys():
            exec('from CI_Zookeeper import CI_Zookeeper')
            self.zk= eval('CI_Zookeeper(**self.config)')
            module_list.append('CI_Zookeeper')
        if 'session' in self.config.keys():
            exec('from CI_Session import CI_Session')
            self.session= eval('CI_Session(**self.config)')
            module_list.append('CI_Session')
        if 'template' in self.config.keys():
            exec('from CI_Template import CI_Template')
            self.tpl= eval('CI_Template(**self.config)')
            module_list.append('CI_Template')




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

        floder_list=['controllers','views','models','helpers','library','config']
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
        if not isinstance(obj,str) and not isinstance(obj,unicode):
            html=json.dumps(obj)
            start_response(str(code), [('Content-Type', 'application/json')] )
        else:
            start_response(str(code), [('Content-Type', 'text/html')] )
            if isinstance(obj,unicode):
                html=unicode.encode(obj,'utf-8')
            else:
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






