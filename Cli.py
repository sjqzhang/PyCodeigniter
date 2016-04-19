#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


from codeigniter import ci
from codeigniter import CI_Cache
import os
import json


class Index:
    def _params(self,param='{}',opts=''):
        params= json.loads(param)
        return params
    def parse_argv(self,argv):
        data={}
        long_args=[]
        short_args=[]
        for v in argv:
            if v.startswith('--'):
                long_args.append(v.replace('--','')+"=")
            elif v.startswith('-'):
                short_args.append(v.replace('-',''))
        opts= getopt.getopt(argv,":".join(short_args)+":",long_args)
        for opt in opts[0]:
            data[opt[0].replace('-','')]=opt[1]
        if len(data)>0:
            return data
        else:
            return argv
    def index(self,param=''):
        ctrl='cli'    
        action='help'
        cm={
          '':'Cli',
          'h':'CliHelp'
        }  
        params=self._params(param)
        if len(params)>2 and params[1].startswith('-'):
            action=params[0]
            para=self.parse_argv(params[1:])
        else:
            ctrl=params[0]
            action=params[0]
            para=self.parse_argv(params[2:])
        return ci.loader.ctrl(ctrl).action(para)
            
     

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
        sql="select cmd from doc group by cmd"
        rows=ci.db.query(sql)
        ret=''
        for row in rows:
            if row['cmd']!=None:
                ret+=str(row['cmd'])+"\n"
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
                    ret+='# docid:  '+str(row['id'])+"\n"+str(row['doc'])+"\n"
                else:
                    ret+=str(row['doc'])+"\n"
                ret+="#"*50
        return ret
        
