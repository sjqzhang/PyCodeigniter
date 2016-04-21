#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


from codeigniter import ci
from codeigniter import CI_Cache
import os
import json
import re
import sys



class Cli:


    def index(self):
        return "hello world"


    def help(self,param=''):
	h='''
        ########## 文件与shell ##############

        cli upgrade   更新 cli 程序
        cli shell -f filename  下载并接行shell指令
        cli listfile   查看文件列表
        cli upload -f filename  上传文件
        cli download -f filename  下载文件
        cli delfile -f filename -k key  删除文件
        
        ########## 环境变量 ##############

        cli addenv -k key -v value  -g group (default)  增加环境变量
        cli getevn  -k key -g group (default) 获取环境变量
        cli delenv   -k key -g group 删除环境变量 
        cli listenv   -g group -e 1 查看某个组的环境变量 默认 default -e 1 导出
        cli updateenv   -k key -v value -g group (default)更新环境变量 

         '''
        return h

    def download(self,file=''):
        if  'f' in params: 
            filename=params['f'] 
        else: 
            return '-f(filename) require' 
        return open('files'+os.path.sep+ file,'rb').read()

    def shell(self,file='',param=''):
        return open('files'+os.path.sep+ file,'rb').read()

    def upgrade(self,param=''):
        return open('cli').read()

    def _params(self,param='{}',opts=''):
        params= json.loads(param)
        return params

    def listfile(self,param=''):
        params=self._params(param) 
        if 'd' in params:
            directory=params['d']
        else:
            directory=''
        directory=directory.replace('.','')
        return "\n".join(os.listdir('files/'+directory))


    def upload(self,**kwargs): 
        file=kwargs['file'] 
        directory=kwargs['dir'] 
        directory=directory.replace('.','')
        path='files/'+directory
        filename=path+'/'+file.filename 
        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.exists(filename): 
            if isinstance(file,str): 
                open(filename,'wb').write(file) 
            else: 
                open(filename,'wb').write(file.file.read()) 
            return 'success' 
        else: 
            return 'file exists' 
 
    def delfile(self,param=''): 
        params=self._params(param) 
        filename='' 
        key='meizu.com' 
        directory='/'
        k='' 
        if  'f' in params: 
            filename=params['f'] 
        else: 
            return '-f(filename) require' 
        if  'k' in params: 
            k=params['k'] 
        else: 
            return '-k(key) require' 
        if  'd' in params: 
            directory=params['d'] 
        if not key==k: 
            return 'key error' 
        directory=directory.replace('.','')
        path='files/'+directory + '/' +filename 
        if os.path.exists(path): 
            os.remove(path) 
            return "sucess" 
        else: 
            return "Not Found" 
    def rexec(self,param=''):
        params=self._params(param)
        ip=''
        cmd=''
        k=''
        key='Mz'
        if 'i' in params:
            ip=params['i']
        else:
            return '-i(ip) require'
        if 'c' in params:
            cmd=params['c']
        else:
            return '-c(command) require'
        if  'k' in params:
            k=params['k']
        else:
            return '-k(key) require'
        if not key==k:
            return 'key error'
        return self._remote_exec(ip,cmd)

    def _remote_exec(self,ip,cmd):
       try:
           import paramiko
           ssh=paramiko.SSHClient()
           ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
           pkey= paramiko.RSAKey.from_private_key_file ('keypath/filename','keypassword')
           try:
               ssh.connect(ip,22,'ops','',pkey)
           except Exception as err:
               self.app.logger.error("PKERROR:"+str(err))
               try:
                   ssh.connect(ip,22,'root','root')
               except Exception as usererr:
                   self.app.logger.error("USERERROR:"+str(err))
                   ssh.connect(ip,16120,'root','root')

           ssh.exec_command('sudo -i')
           ret=[]
           reterr=[]
           if isinstance(cmd,list):
               for c in cmd:
                   stdin, stdout, stderr = ssh.exec_command(cmd)
                   reterr.append("".join(stderr.readlines()))
                   ret.append("".join(stdout.readlines()))
           else:
               stdin, stdout, stderr = ssh.exec_command(cmd)
               reterr=stderr.readlines()
               ret=stdout.readlines()

           if len(reterr)>0:
               return "".join(reterr)
           return "".join(ret)
       except Exception as er:
           self.app.logger.error(er)
           return str(er)
       finally:
           try:
              ssh.close()
           except Exception as err:
               pass

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
    def listenvgroup(self,param=''):
        params=self._params(param)
        sql="select group_ from env group by group_"
        rows=ci.db.query(sql)
        ret=''
        for row in rows:
            if row['group_']!=None:
                ret+=str(row['group_'])+"\n"
        return ret
                
        return ret
    def listenv(self,param=''):
        params=self._params(param)
        group='default'
        export='0'
        if 'g' in params:
            group=params['g']
        if 'e' in params:
            export=params['e']
        sql="select key_,value_ from env where `group_`='%s'" % (group)
        rows=ci.db.query(sql)
        if len(rows)==0:
            return '(error) not found'
        ret=''
        for row in rows:
            if export=='1': 
                ret+='export '+row['key_']+'='+row['value_']+"\n"
            else:
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
        
################################################ doc ###############################################
    def _checkdoc(self,param=''):
        params=self._params(param)
        id=''
        if 'i' in params:
            id=params['i']
        else:
            return '-k(key) require'
        rows=ci.db.query("select * from doc where `id`='%s'"% (id))
        if len(rows)>0:
            return True
        else:
            return False
    def listdoc(self,param=''):
        params=self._params(param)
        if 'k' in params:
            return self.getdoc(param)
        sql="select cmd from doc group by cmd"
        rows=ci.db.query(sql)
        ret=''
        for row in rows:
            if row['cmd']!=None:
                ret+=unicode(row['cmd'])+"\n"
        return ret
                
        return ret
            
    def adddoc(self,param=''):
        params=self._params(param)
        cmd=''
        doc=''
        remark=''
        if 'c' in params:
            cmd=params['c']
        if 'd' in params:
            doc=params['d']
            if cmd=='':
                cmd=doc.strip().split(" ")[0]
        else:
            return '-d(document) require'
        if 'r' in params:
            remark=params['r']
        sql='''INSERT INTO doc 
	(
	cmd, 
	doc, 
	remark
	)
	VALUES
	(
	'{cmd}', 
	'{doc}', 
	'{remark}'
	)'''
        ci.db.query(sql,{'cmd':cmd,'doc':doc,'remark':remark})
        #ci.db.insert('doc',{'cmd':cmd,'doc':doc,'remark':remark})
        return 'ok'
    def deldoc(self,param=''):
        params=self._params(param)
        id=''
        if 'i' in params:
            id=params['i']
        else:
            return '-i(id) require'
        if self._checkenv(param):
            ci.db.delete('doc',{'id':id})
            return 'ok'
        else:
            return '(error)key no found'
    def getdoc(self,param=''):
        params=self._params(param)
        key=''
        if 'k' in params:
            key=params['k']
        else:
            return '-k(keyword) require'
        if 'a' in params:
            rows= ci.db.query("select id,doc from doc where  `cmd` like '%%%s%%' or doc like '%%%s%%'"% (key,key))
        else:
            rows= ci.db.query("select id,doc from doc where  `cmd`='%s'"% (key))
        ret=''
        outid='i' in params
        for row in rows:
            if row['doc']!=None:
                if outid:
                    ret+='# docid:  '+unicode(row['id'])+"\n"+unicode(row['doc'])+"\n"*3
                else:
                    ret+=str(row['doc'])+"\n"*3
                #ret+="#"*50+"\n"
        return ret
        
