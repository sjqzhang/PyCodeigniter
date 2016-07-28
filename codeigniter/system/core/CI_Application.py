#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


import sys
import os
import json
import imp
import urllib
sys.path.insert(0,os.path.dirname(__file__))
try:
    import urllib2
except:
    import urllib.request as urllib2
import hashlib

import platform

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


try:
    import pyquery
except Exception as er:
    pass
try:
    import uuid
except Exception as er:
    pass


is_install_gevent=False
try:
    from gevent import monkey
    monkey.patch_all()
    from gevent.pywsgi import WSGIServer
    is_install_gevent=True
except Exception as er:
    pass


try:
    from cookielib import CookieJar
except:
    import http.cookiejar as CookieJar
import re
import zlib



import pdb
from threading import local
class CI_CLASS(object):

    def __getattr__(self,attr):
        ci = CI_Application.application_instance
        if hasattr(ci,attr):
            return getattr(ci,attr)
        return None

CI = CI_CLASS()


from CI_Response import CI_Response

class CI_Application(object):
    application_instance=None
    try:
        cj = CookieJar()
    except:
        cj =CookieJar.CookieJar()
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
        self.is_threads = False
        self.local = local()
        self.ctx = local()
        self._is_python3=None

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

    def set_header(self,key,value):
        if type(key) == str and type(value):
            self.local.response.headers.append( (key,value) )

    @property
    def is_python3(self):
        if self._is_python3!=None:
            return self._is_python3
        self._is_python3=platform.version().split('.')[0]=='3'
        return self._is_python3

    def get(self,key):
        if key in self.instances.keys():
            return self.instances[key]
    def set(self,key,value):
        self.instances[key]=value

    def init(self):
        if self.config_file!=None:
            if PY2:
                execfile(self.config_file,{},self.config)
            if PY3:
                exec(open(self.config_file).read(),{}, self.config)
                self.config=self.config.get('config')
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

        exec('from CI_Hook import CI_Hook')
        self.hook= eval('CI_Hook()')
        self.hook.call_pre_system()

        if 'use_threads' in self.config.keys():
            self.is_threads = self.config['use_threads']
        for conf in self.config.keys():
            if isinstance(self.config[conf],dict):
                self.config[conf]['app']=self
        exec('from CI_Logger import CI_Logger')
        self.logger= eval('CI_Logger(**self.config["log"])')
        module_list=['CI_Loader','CI_Mail','CI_Router','CI_Input','CI_Cache','CI_DB']

        cache_type='memory'
        for m in module_list:
            try:
                exec('from '+ m +' import '+m)
            except Exception as err:
                self.logger.error(err)
        self.input= eval('CI_Input(**self.config)')

        exec('from CI_Cookie import CI_Cookie')
        self.cookie= eval('CI_Cookie(**self.config)')
        module_list.append('CI_Cookie')

        if 'db' in self.config.keys():
            # if 'type' in self.config['db'] and self.config['db']['type']=='sqlite' :
            #     exec('from CI_Sqlite import CI_Sqlite')
            #     exec('from CI_DBActiveRec import CI_DBActiveRec')
            #
            #     self.db= eval('CI_Sqlite(**self.config["db"])')
            #     module_list.append('CI_Sqlite')
            #     module_list.append('CI_DBActiveRec')
            #
            # else:
            exec('from CI_DB import CI_DB')
            exec('from CI_DBActiveRec import CI_DBActiveRec')

            self.db= eval('CI_DB(**self.config["db"])')
            module_list.append('CI_DB')
            module_list.append('CI_DBActiveRec')
        else:
            self.logger.warn('db not config')
        self.static = None
        self.router= eval('CI_Router(**self.config)')
        if 'mail' in self.config.keys():
            self.mail= eval('CI_Mail(**self.config["mail"])')
            module_list.append('CI_Mail')
        if 'cache' in self.config.keys():
            self.cache= eval('CI_Cache(**self.config)')
            if 'type' in self.config['cache']:
                cache_type=self.config['cache']['type']
        if 'server' in self.config.keys():
            if 'static_dir' in self.config['server']:
                exec('from CI_Static import CI_Static')
                self.static = eval('CI_Static(**self.config)')


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
        # self._load_ci_cls()

    def _load_ci_cls(self):
        try:
            path_core=self.system_path+os.path.sep+'core'
            files= os.listdir(path_core)
            sys.path.insert(0,path_core)
            for file in files:
                if file.endswith('.py') and file.startswith('CI_'):
                    try:
                        mod=self.loader.load_file(path_core+os.path.sep+ file)
                        cls=file.replace('.py','')
                        if hasattr(mod,cls):
                            self.loader.regcls(cls,getattr(mod,cls))
                    except Exception as e:
                       pass
        except Exception as er:
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




    def get_logger(self,name):
        return self.getLogger(name)

    def getLogger(self,name=None):
        if name==None:
            return self.logger
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
        if PY2 and isinstance(s,unicode):
            s=s.encode('utf-8')
        m.update(s)
        return m.hexdigest()

    def uuid(self):
        return str(uuid.uuid4())

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

    def request( self, url,data=None,headers={},proxys={},timeout=15,gzip=False):
        if len(proxys)>0:
            proxy_handler=urllib2.ProxyHandler(proxys)
            CI_Application.proxy_handler=proxy_handler

        opener = urllib2.build_opener(CI_Application.proxy_handler,urllib2.HTTPCookieProcessor(CI_Application.cj))
        if not 'User-Agent' in headers.keys():
            headers['User-Agent']='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36'
        if gzip:
            headers['Accept-Encoding']='gzip, deflate'
        if data!=None:
            data = urllib.urlencode(data)
        while len(opener.addheaders)>0:
            opener.addheaders.pop()
        for k,v in headers.iteritems():
            opener.addheaders.append((k,v))
        response = opener.open(url,data=data,timeout=timeout)
        if 'Content-Encoding' in response.headers:
            if response.headers['Content-Encoding'].lower()=='gzip':
                unzip=True


        filesize=0
        if 'Content-Length' in response.headers:
            filesize= response.headers['Content-Length']
            import tempfile
            if int(filesize)>10*1024*1024:
                tmp=None
                try:
                    tmp= tempfile.TemporaryFile()
                    file_size_dl = 0
                    block_sz = 8192
                    while True:
                        buffer = response.read(block_sz)
                        if not buffer:
                            break
                        file_size_dl += len(buffer)
                        tmp.write(buffer)
                        # status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / filesize)
                        # status = status + chr(8)*(len(status)+1)
                        # print status,
                    tmp.seek(0)
                    return tmp.read()
                except Exception as er:
                    self.logger.error(er)
                finally:
                    try:
                        tmp.close()
                    except Exception as er:
                        pass
        content=response.read()
        if gzip and unzip:
            content= zlib.decompress( content , 16+zlib.MAX_WBITS)

        if 'Content-Type' in response.headers:
            charset=re.findall(r'charset\=(\w+)',response.headers['Content-Type'],re.IGNORECASE)
            if len(charset)>0:
                return content.decode(charset[0],'ignore')
            elif len(re.findall(r'text/html',response.headers['Content-Type'],re.IGNORECASE))>0:
                charset= re.findall(r'<meta[\s\S]*?charset=([\w\-]+)[\s\S]*?>',content,re.IGNORECASE)
                if len(charset)>0:
                    if charset[0].lower()=='gb2312':
                        charset[0]='gbk'
                    content=content.decode(charset[0])
                else:
                    content=content.decode('utf-8')
                return content
            else:
                return content
        else:
            return content


    def request_query(self,url,data=None,selector=''):
        html=self.request(url,data)
        return pyquery.PyQuery(selector,html)

    def pq(self,obj,selector=None):
        if selector==None:
            return pyquery.PyQuery(obj)
        else:
            return pyquery.PyQuery(selector,obj)

    def setresult(self,code,content):
        self.local.response.status = code
        self.local.response.body = content

    def set200(self,content):
        self.local.response.status = '200 OK'
        self.local.response.body = content

    def set404(self,content=""):
        self.local.response.status = "404 Not Found"
        self.local.response.body = "Not Found" if "" ==  content else content

    def set500(self,content=""):
        self.local.response.status = "500 Internal server error"
        self.local.response.body = "Server Error,Please see log file" if "" ==  content else content

    def __call__(self, environ, start_response):
        return self.application(environ,start_response)
    def application(self, environ, start_response):
        try:
            self.local.response = CI_Response()
            self.local.env=environ
            self.cookie.parse_cookie(environ)
            # print self.local.response.cookies
            self.router.wsgi(environ)
            self.hook.call_display_override(environ)
            code = self.local.response.status
            content = self.local.response.body
            if self.cookie:
                self.cookie.result_cookie()
            if PY2 and isinstance(content,unicode):
                content=unicode.encode(content,'utf-8','ignore')
            if PY2 and (not type(content) in [str,unicode]):
                content = json.dumps(content)
            if PY3:
                if isinstance(content,str):
                    content=content.encode('utf-8')
                else:
                    content = json.dumps(content).encode('utf-8')
            start_response(str(code),self.local.response.headers)
            self.local.response = None
            if PY2:
                return [str(content)]
            if PY3:
                return [content]
        except Exception as er:
            self.set500(str(er))
            return [str(self.local.response.body)]





    def start_server(self):
        msg="server listen to : "+str(self.config['server']['port'])
        print(msg)
        self.logger.info(msg)
        if is_install_gevent:
            print("running gevent wsgiserver ...")
            WSGIServer((self.config['server']['host'],self.config['server']['port']), self.application).serve_forever()
        else:
            from wsgiref.simple_server import make_server
            httpd=make_server(self.config['server']['host'],self.config['server']['port'],self.application)
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






