#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import sys
import os
import json
import imp
import urllib
import urllib2
import hashlib

try:
    import pyquery
except Exception as er:
    pass


is_gevent=False

try:
    from gevent import monkey; monkey.patch_all()
    from gevent.pywsgi import WSGIServer
    is_gevent=True
except Exception as er:
    pass

from cookielib import CookieJar
import re



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
    cj = CookieJar()
    proxy_handler=urllib2.ProxyHandler({})
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
        self.redis=None
        self.loggers={}
        self.instances={}
        self.memcache=None
        self.session=None
        self.cookie=None
        self._app_create(application_path)
        CI_Application.application_instance = self
        self.init()


    # def __setitem__(self, key, value):
    #     if not key in ['loader','tpl','instances','db','config','mail','zk','redis','memcache',
    #                 'cron','server','cache','logger','loggers']:
    #         self[key]=value
    #
    #
    # def __getattr__(self, item):
    #     if hasattr(self,item):
    #         return getattr(self,item)


    def get(self,key):
        if key in self.instances.keys():
            return self.instances[key]
    def set(self,key,value):
        self.instances[key]=value

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

        cache_type='memory'
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
            if 'type' in self.config['cache']:
                cache_type=self.config['cache']['type']
        if 'server' in self.config.keys() and 'fastpy' in self.config['server'] and  self.config['server']['fastpy'] :
            exec('from CI_Server import CI_Server')
            self.server= eval('CI_Server(**self.config)')
            module_list.append('CI_Server')

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
        if 'redis' in self.config.keys():
            exec('from CI_Redis import CI_Redis')
            self.redis= eval('CI_Redis(**self.config)')
            module_list.append('CI_Redis')
            if cache_type=='redis':
                self.cache.set_cache(self.redis)
        if 'memcache' in self.config.keys():
            exec('from CI_Memcache import CI_Memcache')
            self.memcache= eval('CI_Memcache(**self.config)')
            module_list.append('CI_Memcache')
            if cache_type=='memcache':
                self.cache.set_cache(self.memcache)
        if 'cron' in self.config.keys():
            exec('from CI_Cron import CI_Cron')
            self.cron= eval('CI_Cron(**self.config)')
            module_list.append('CI_Cron')

        #must be instance last
        self.loader= eval('CI_Loader(**self.config)')

        if 'cron' in self.config.keys():
            self.cron.init()






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

    def merge_conf(self,input_config={},default_config={}):
        for key,value in default_config.iteritems():
            if not key in input_config.keys():
                input_config[key]=value
        if 'app' in input_config and isinstance(input_config['app'],CI_Application):
            del input_config['app']
        return input_config


    def request_hander(self, environ, start_response):
        html=''
        cookie=[]


        code,obj=self.router.wsgi_route(environ)
        if 'session' in self.config.keys():
            cookie = self.cookie.result_cookie()
        if not isinstance(obj,str) and not isinstance(obj,unicode):
            html=json.dumps(obj)
            start_response(str(code), [('Content-Type', 'application/json')] +cookie )
        else:
            start_response(str(code), [('Content-Type', 'text/html')] +cookie )
            if isinstance(obj,unicode):
                html=unicode.encode(obj,'utf-8')
            else:
                html=obj
        return [str(html)]

    def get_logger(self,name):
        return self.getLogger(name)

    def getLogger(self,name):
        if name in self.loggers:
            return self.loggers[name]
        if name in self.config:
            cfg=self.config[name]
            cfg['name']=name
            exec('from CI_Logger import CI_Logger')
            # logger=self.loader.cls('CI_Logger')(**cfg)
            logger= eval('CI_Logger(**cfg)')
            self.loggers[name]=logger
            return logger
        else:
            self.logger.warn('config for %s not found'%(name) )


    def md5(self,s):
        m=hashlib.md5()
        if isinstance(s,unicode):
            s=s.encode('utf-8')
        m.update(s)
        return m.hexdigest()

    # def request( self, url,data=None,headers={}):
    #         html='';
    #         if not 'User-Agent' in headers.keys():
    #             headers['User-Agent']='Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
    #         try:
    #             if data!=None and len(data)>0:
    #                 data=urllib.urlencode(data)
    #             req = urllib2.Request(
    #                 url =url,
    #                 headers = headers,
    #                 data=data
    #             )
    #             html=urllib2.urlopen(req,timeout=15).read()
    #         except Exception as er:
    #             self.logger.error(er)
    #         return html

    def request( self, url,data=None,headers={},proxys={},timeout=15):
        if len(proxys)>0:
            proxy_handler=urllib2.ProxyHandler(proxys)
            CI_Application.proxy_handler=proxy_handler

        opener = urllib2.build_opener(CI_Application.proxy_handler,urllib2.HTTPCookieProcessor(CI_Application.cj))
        if not 'User-Agent' in headers.keys():
                headers['User-Agent']='Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        if data!=None:
            data = urllib.urlencode(data)
        for k,v in headers.iteritems():
            opener.addheaders.append((k,v))
        response = opener.open(url,data=data,timeout=timeout)
        if 'Content-Type' in response.headers:
            charset=re.findall(r'charset\=(\w+)',response.headers['Content-Type'],re.IGNORECASE)
            if len(charset)>0:
                return response.read().decode(charset[0],'ignore')
            else:
                return  response.read()
        else:
            return response.read()


    def request_query(self,url,data=None,selector=''):
        html=self.request(url,data)
        return pyquery.PyQuery(selector,html)

    def pq(self,obj):
        return pyquery.PyQuery(obj)

    def start_server(self):
        msg="server listen to : "+str(self.config['server']['port'])
        print(msg)
        self.logger.info(msg)
        if is_gevent:
            port=self.config['server']['port']
            host=self.config['server']['host']
            WSGIServer((host, port), self.request_hander).serve_forever()
        else:
            from wsgiref.simple_server import make_server
            httpd=make_server(self.config['server']['host'],self.config['server']['port'],self.request_hander)
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






