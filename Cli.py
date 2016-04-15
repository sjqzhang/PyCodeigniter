#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


from codeigniter import ci
from codeigniter import CI_Cache
import os
import json

class Cli:


    def index(self):
        return "hello world"


    def help(self,param=''):
	h='''
        cli upgrade   更新 cli 程序
        cli shell   下载并接行shell指令
        cli listfile   查看文件列表
        cli download   下载文件
        cli delfile -f filename -k key  删除文件

        cli addenv -k key -v value  -g group (default)  增加环境变量
        cli getevn  -k key -g grup (default) 获取环境变量
        cli delenv   -k key -g grup 删除环境变量 
        cli listenv   -g grup 查看某个组的环境变量 默认 default
        cli updateenv   -k key -v value -g group (default)更新环境变量 

         '''
        return h

    def download(self,file=''):
        return open('files'+os.path.sep+ file,'rb').read()

    def shell(self,file='',param=''):
        return open('files'+os.path.sep+ file,'rb').read()

    def upgrade(self,param=''):
        return open('cli').read()

    def _params(self,param='{}',opts=''):
        params= json.loads(param)
        return params

    def listfile(self,param=''):
        return "\n".join(os.listdir('files'))


    def upload(self,**kwargs): 
        file=kwargs['file'] 
        filename='files/'+file.filename 
        if not os.path.exists(filename): 
            if isinstance(file,str): 
                open(filename,'wb').write(file) 
            else: 
                open('files/'+file.filename,'wb').write(file.file.read()) 
            return 'success' 
        else: 
            return 'file exists' 
 
    def delfile(self,param=''): 
        params=self._params(param) 
        filename='' 
        key='meizu.com' 
        k='' 
        if  'f' in params: 
            filename=params['f'] 
        else: 
            return '-f(filename) require' 
        if  'k' in params: 
            k=params['k'] 
        else: 
            return '-k(key) require' 
        if not key==k: 
            return 'key error' 
        path='files/'+filename 
        if os.path.exists(path): 
            os.remove(path) 
            return "sucess" 
        else: 
            return "Not Found" 

################################################env###############################################
    def _checkenv(self,param=''):
        params=self._params(param)
        key=''
        group='default'
        if 'g' in params:
            group=params['g']
        if 'k' in params:
            key=params['k']
        else:
            return '-k(key) require'
        rows=ci.db.query("select * from env where `group_`='%s' and `key_`='%s'"% (group,key))
        if len(rows)>0:
            return True
        else:
            return False
    def listenv(self,param=''):
        params=self._params(param)
        group='default'
        if 'g' in params:
            group=params['g']
        sql="select key_,value_ from env where `group_`='%s'" % (group)
        rows=ci.db.query(sql)
        if len(rows)==0:
            return '(error) not found'
        ret=''
        for row in rows:
            ret+=row['key_']+'='+row['value_']+"\n"
        return ret
    def updateenv(self,param=''):
        params=self._params(param)
        key=''
        value=''
        group='default'
        if 'k' in params:
            key=params['k']
        else:
            return '-k(key) require'
        if 'g' in params:
            group=params['g']
        if 'v' in params:
            value=params['v']
        else:
            return '-v(value) require'
        if not self._checkenv(param):
            return '(error)key not is exsit'  
        ci.db.update('env',{'value_':value},{'key_':key,'group_':group})
        return 'ok'
            
    def addenv(self,param=''):
        params=self._params(param)
        key=''
        value=''
        
        group='default'
        if 'k' in params:
            key=params['k']
        else:
            return '-k(key) require'
        if 'g' in params:
            group=params['g']
        if 'v' in params:
            value=params['v']
        else:
            return '-v(value) require'
        if self._checkenv(param):
            return '(error)key is exsit'  
        ci.db.insert('env',{'key_':key,'value_':value,'group_':group})
        return 'ok'
    def delenv(self,param=''):
        params=self._params(param)
        key=''
        group='default'
        if 'g' in params:
            group=params['g']
        if 'k' in params:
            key=params['k']
        else:
            return '-k(key) require'
        if self._checkenv(param):
            ci.db.delete('env',{'key_':key,'group_':group})
            return 'ok'
        else:
            return '(error)key no found'
    def getenv(self,param=''):
        params=self._params(param)
        key=''
        group='default'
        if 'g' in params:
            group=params['g']
        if 'k' in params:
            key=params['k']
        else:
            return '-k(key) require'
        if not self._checkenv(param):
            return '(error)key no found'
        return ci.db.scalar("select value_ from env where `group_`='%s' and `key_`='%s'"% (group,key))['value_']
