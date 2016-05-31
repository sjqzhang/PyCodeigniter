#!/usr/bin/env python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'


from codeigniter import ci
from codeigniter import cache
from codeigniter import CI_Cache
import os
import json
import re
import sys
import time
import base64
# from sql4json.sql4json import *

# OP_NOT_VALID = -1
# OP_EQUAL = 1
# OP_NOT_EQUAL = 2
#
# class Match_Helper():
#     def __init__(self, content_dict, is_regex=False):
#
#         self.content = {}
#         for k, val in content_dict.iteritems():
#             self.content[k.lower()] = val.lower()
#
#         self.is_regex = is_regex
#         self.expr = None
#
#     @staticmethod
#     def check_pattern(expr):
#         if not expr:
#             return False
#
#         lcount = expr.count('(')
#         rcount = expr.count(')')
#         return lcount == rcount
#
#     def find_operator(self, expr):
#         """
#         返回 op_type， key, value
#         :param expr:
#         :return:
#         """
#         length = len(expr)
#         idx_e = expr.find('=') if expr.find('=') != -1 else length
#         idx_ne = expr.find('<>') if expr.find('<>') != -1 else length
#         idx = min(idx_e, idx_ne)
#         if idx == length:
#             return -1, '', ''
#
#         key = expr[:idx].strip().lower()
#         val = expr[idx + (1 if idx == idx_e else 2):].strip().lower()
#         return (OP_EQUAL if idx == idx_e else OP_NOT_EQUAL), key, val
#
#     def compute(self, expr):
#         expr = expr.strip()
#         op_type, op_key, op_val = self.find_operator(expr)
#         if op_type == OP_NOT_VALID:
#             return False  # TODO 表达式不合法，这里应该终止计算，先做返回False处理
#         val_content = self.content.get(op_key, '').lower()
#
#         bfilter, ret = self._filter(op_key, op_val, val_content, op_type)
#         if bfilter:
#             return ret
#         else:
#             if op_type == OP_EQUAL:
#                 return self.compute_equal(op_val, val_content, self.is_regex)
#             else:
#                 return self.compute_not_equal(op_val, val_content, self.is_regex)
#
#     def _filter(self, key, val_pattern, val_content, op_type):
#         if self.is_regex or key != 'hostgroup':
#             return False, False
#
#         hostgroup_list = [s.strip() for s in val_content.split(',')]
#         if op_type == OP_EQUAL:
#             return True, val_pattern in hostgroup_list
#         else:
#             return True, val_pattern not in hostgroup_list
#
#     def compute_equal(self, val_pattern, val_content, is_regex):
#         if self.is_regex:
#             return True if re.search(val_pattern, val_content, re.IGNORECASE) else False
#         else:
#             return True if val_content == val_pattern else False
#         pass
#
#     def compute_not_equal(self, val_pattern, val_content, is_regex):
#         if self.is_regex:
#             return True if not re.search(val_pattern, val_content, re.IGNORECASE) else False
#         else:
#             return True if val_content != val_pattern else False
#         pass
#
#     # pattern = '(host=MZKJ-PC-02876)and(hostgroup=Discovered hosts)and((level=Warning)or(Critical))'
#     def calculate(self):
#         self.expr = self.expr.strip()
#         if len(self.expr) == 0:
#             return False
#
#         if self.expr[0] == '(':
#             self.expr = self.expr[1:]
#             ret = self.calculate()
#             assert self.expr[0] == ')'
#             self.expr = self.expr[1:].lstrip()
#
#             if self.expr.startswith('and'):
#                 self.expr = self.expr[3:]
#                 return self.calculate() and ret
#             elif self.expr.startswith('or'):
#                 self.expr = self.expr[2:]
#                 return self.calculate() or ret
#             else:
#                 return ret
#         else:
#             ridx = self.expr.find(')')
#             if ridx == -1:
#                 return self.compute(self.expr)
#             ret = self.compute(self.expr[:ridx])
#             self.expr = self.expr[ridx:]
#             return ret
#
#     def match(self, expr):
#         expr = expr.strip()
#         if not self.check_pattern(expr):
#             return False
#
#         self.expr = expr
#         return self.calculate()
#
#
# class Match:
#     def __init__(self):
#         pass
#
#     def match(self, pattern, content_dict, is_regex=False):
#         matcher = Match_Helper(content_dict, is_regex)
#         if isinstance(pattern, (tuple, list)):
#             ret = {}
#             for i in range(len(pattern)):
#                 ret[i] = matcher.match(pattern[i])
#             return ret
#         else:
#             return matcher.match(pattern)
#
#     def is_valid_pattern(self, pattern):
#         return Match_Helper.check_pattern(pattern)


# if __name__ == '__main__':
#     pattern = [
#         '(((hostname=MZKJ-PC-02876)))',
#         '(hostname=MZKJ-CentOS7-17.16.137.8) and ( hostgroup=Discovered hosts, Linux servers)and(((level=Warning)or(level=Critical)))'
#     ]
#     content = "event_time=14:58:57|event_value=1|level=Warning|expression={MZKJ-CentOS7-17.16.137.8:system.cpu.util[0,,avg1].last()}>5|hostname=MZKJ-CentOS7-17.16.137.8|hostgroup=Discovered hosts, Linux servers|templatename=Template OS Linux|ip=172.16.137.8|item_name=Processor load (1 min average per core)|item_value=6.968583"
#
#     import sys
#
#     sys.path.append('..')
#     # from helpers.help import Helper
#
#     # print content
#     start=time.time()
#     for i in xrange(1,100000):
#         Match().match(pattern,{'event_value':'Linux','expression':'abc'})
#     print(time.time()-start)



############################# new exp ############################as



class Expr:
    def __init__(self, expr):
        self.op_map = {
            '=': self._equal_,
            '!=': self._not_equal,
            '<>': self._not_equal,
            'like': self._like
        }
        self.key, self.op, self.val = self.__parser(expr)
        self.func = self.op_map[self.op]

    def __parser(self, expr):
        op = map(lambda x: [expr.find(x), x], filter(lambda x: x in expr, self.op_map.keys()))
        assert len(op) >= 1

        op = min(op)
        return str(expr[:op[0]]).strip().lower(), str(op[1]).strip().lower(), str(expr[op[0] + len(op[1]):]).strip().lower()

    def _equal_(self, fst_val, sec_val):
        return fst_val == sec_val

    def _like(self,fst_val,sec_val):
        return fst_val in sec_val


    def _not_equal(self, fst_val, sec_val):
        return fst_val != sec_val

    def compute(self, data_dict):
        v=data_dict.get(self.key, '')
        if isinstance(v,unicode):
            v = v.encode('utf-8')
        sec_val = str(v).lower()
        return self.func(self.val, sec_val)


class Matcher:
    def __init__(self, pattern_expr):
        self.raw_pattern_expr = pattern_expr
        self.postfix_expr_list = self.__translate_to_postfix_expr(pattern_expr)
        pass


    def __is_startswith_op(self, pattern_expr):
        if pattern_expr.startswith('('):
            return True, '(', pattern_expr[1:]
        elif pattern_expr.startswith('or'):
            return True, 'or', pattern_expr[2:]
        elif pattern_expr.startswith('and'):
            return True, 'and', pattern_expr[3:]
        else:
            return False, '', pattern_expr

    def __translate_to_postfix_expr(self, pattern_expr):
        postfix_expr_list = []
        tmp_stack = []

        while True:
            pattern_expr = pattern_expr.strip()
            if len(pattern_expr) <= 0:
                break

            is_op, op, pattern_expr = self.__is_startswith_op(pattern_expr)
            if is_op:
                tmp_stack.append(op)
            else:
                idx = pattern_expr.find(')')
                if idx != 0:
                    postfix_expr_list.append(Expr(pattern_expr if idx == -1 else pattern_expr[:idx]))
                pattern_expr = pattern_expr[idx + 1:]

                while True:
                    t = tmp_stack.pop()
                    if t == '(':
                        break
                    postfix_expr_list.append(t)

        while len(tmp_stack) > 0:
            postfix_expr_list.append(tmp_stack.pop())

        print postfix_expr_list
        return postfix_expr_list


    def calc(self, data_dict):
        tmp_list = []
        for i in range(len(self.postfix_expr_list)):
            op = self.postfix_expr_list[i]
            if isinstance(op, Expr):
                tmp_list.append(op.compute(data_dict))
            else:
                fst_val = tmp_list.pop()
                sec_val = tmp_list.pop()
                tmp_list.append((fst_val and sec_val) if op == 'and' else (fst_val or sec_val))
        return tmp_list[0]


class Match_Utils:
    def __init__(self):
        pass

    def Match(self, data_dict, pattern_expr):
        return Matcher(pattern_expr).calc(data_dict=data_dict)




def auth(func):
    def decorated(*arg,**kwargs):
        if not 'HTTP_AUTH_UUID' in ci.local.env:
            return "(error)unauthorize1"
        if ci.cache.get(ci.local.env['HTTP_AUTH_UUID'])==None:
            return "(error)unauthorize"
        return func(*arg,**kwargs)
    return decorated







class Cli:

    def __init__(self):
        self.cmdkeys={}
        pass



    @auth
    def index(self,param=''):
        # print ci.local.env
        #ci.set_header('WWW-Authenticate','Basic realm="Authentication System"')
        #ci.set_header('HTTP/1.0 401 Unauthorized')
        # sys.exit(0)
        return "hello world".strip()
    def abc(self,param='',**kwargs):
        # print ci.local.env
        #ci.set_header('WWW-Authenticate','Basic realm="Authentication System"')
        #ci.set_header('HTTP/1.0 401 Unauthorized')
        # sys.exit(0)
        print kwargs
        return "hello world".strip()

    def help(self,param=''):
        h='''
        ########## 文件与shell ##############

        cli upgrade   更新 cli 程序
        cli shell -f filename  下载并接行shell指令
        cli listfile   查看文件列表
        cli upload -f filename [-d directory] 上传文件
        cli download -f filename [-d directory] [-o path/to/save]  下载文件
        cli delfile -f filename -k key  删除文件

        ########## 环境变量 ##############

        cli addenv -k key -v value  -g group (default)  增加环境变量
        cli getevn  -k key -g group (default) 获取环境变量
        cli delenv   -k key -g group 删除环境变量
        cli listenv   -g group -e 1 查看某个组的环境变量 默认 default -e 1 导出
        cli updateenv   -k key -v value -g group (default)更新环境变量
         '''
        return h


    def getetcd(self,param=''):
        return {'server':['172.16.16.113:4001'],'prefix':'/keeper'}

    def feedback_result(self,param=''):
        print(param)
        data=json.loads(param)['param']
        if 'index' in data.keys() and str(data['index']) in self.cmdkeys.keys():
            self.cmdkeys[str(data['index'])]=data['result']
        ci.logger.info("ip:%s,result:\n%s"%(data['ip'],data['result']))


    def cmd(self,param=''):
        try:
            params=self._params(param)
            etcd=self.getetcd(param)
            cmd=''
            ip=''
            timeout=3

            if  'c' in params:
                cmd=params['c']
            else:
                return '-c(cmd) require'
            if  'i' in params:
                ip=params['i']
            else:
                return '-i(ip) require'
            if  't' in params:
                timeout= float( params['t'])
            import urllib2,urllib
            data={'value':cmd.encode('utf-8')}
            data=urllib.urlencode(data)
            req = urllib2.Request(
                    url ="http://%s/v2/keys%s/servers/%s/"%(etcd['server'][0],etcd['prefix'],ip),
                    data=data
            )
            req.get_method = lambda: 'POST'
            # print urllib2.urlopen(req,timeout=10).read()
            ret=json.loads(urllib2.urlopen(req,timeout=10).read())


            # print ret
            index=str(ret['node']['createdIndex'])
            self.cmdkeys[index]=''
            start=time.time()
            if ret['node']['value']==cmd:
                while True:
                    if (time.time()-start> timeout) or self.cmdkeys[index]!='':
                        break
                    else:
                        time.sleep(0.1)
                if self.cmdkeys[index]!='':
                    ret=self.cmdkeys[index]
                    del self.cmdkeys[index]
                    return ret
                return '(success) submit command success'
            else:
                return '(unsafe) submit command success '
        except Exception as er:
            print er
            return 'fail'
            pass




    def disableuser(self,param=''):
        return self._userstatus(param,0)
    def enableuser(self,param=''):
        return self._userstatus(param,1)
    def _userstatus(self,param='',status=0):
        params=self._params(param)
        user=''
        uuid='(error) not login'
        if  'u' in params:
            user=params['u']
        else:
            return '-u(user) require'
        data={'user':user,'status':status}
        ci.db.query("update user set status='{status}' where user='{user}'",data)
        return 'success'


    def dispatch_cmd(self,param=''):
        params=self._params(param)
        if 'i' not in params:
             return '-i(ip) require'

        return 'ls /data';








    def register(self,param=''):
            params=self._params(param)
            user=''
            pwd=''
            uuid='(error) not login'
            if  'u' in params:
                user=params['u']
            else:
                return '-u(user) require'
            if  'p' in params:
                pwd=params['p']
            else:
                return '-p(password) require'
            data={'user':user}

            if ci.db.scalar("select count(1) as cnt from user where user='{user}'",data)['cnt']>0:
                return "(error)user exist"
            data={'user':user,'pwd':ci.md5(pwd) }
            ci.db.query("insert into user(user,pwd) values('{user}','{pwd}')",data)
            return 'success'

    def login(self,param=''):
        params=self._params(param)
        user=''
        pwd=''
        ip=''
        uuid='(error) user or password error '
        if  'u' in params:
            user=params['u']
        else:
            return '-u(user) require'
        if  'p' in params:
            pwd=params['p']
        else:
            return '-p(password) require'
        if  'i' in params:
            ip=params['i']
        data={'user':user,'pwd':ci.md5(pwd)}
        is_exist=ci.db.scalar("select status from user where user='{user}' and pwd='{pwd}' limit 1 offset 0",data)
        udata={'user':user,'lasttime':time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),'ip':ip}
        if is_exist!=None:
            if is_exist['status']!=1:
                return '(error) user not in actvie status'
            ci.db.query("update user set logincount=logincount+1,lasttime='{lasttime}',ip='{ip}' where user='{user}'",udata)
            uuid=str(ci.uuid())
            ci.cache.set(uuid,user)
        else:
            ci.db.query("update user set logincount=logincount+1,failcount=failcount+1,lasttime='{lasttime}',ip='{ip}' where user='{user}'",udata)

        return str(uuid)


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
        if 'k' in params:
            id=params['k']
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
                ret+=(row['cmd'].encode('utf-8'))+"\n"
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
        if 'k' in params:
            id=params['k']
        else:
            return '-k(id) require'
        if self._checkdoc(param):
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
                    ret+='# docid:  '+str(row['id'])+"\n"+(row['doc'].encode('utf-8'))+"\n"*3
                else:
                    ret+=str(unicode.encode(row['doc'],'utf-8','ignore'))+"\n"*3
                #ret+="#"*50+"\n"
        return ret

################################################ tags ###############################################
    def addtag(self,param=''):
        params=self._params(param)
        table=''
        tag=''
        if 'tag' in params:
            tag=params['tag']
        else:
            return '--tag(tag) require'
        if 'table' in params:
            table=params['table']
        else:
            return '--table(table name) require'
        if tag.find('=')==-1:
            return 'tag must be "key=value"'
        body={}
        for t in tag.split(';'):
            kv=t.split('=')
            if len(kv)==2:
                body[kv[0]]=kv[1]
        row=ci.db.scalar("select id,body from tags where tbname='{tbname}' limit 1 offset 0",{'tbname':table})
        if row==None:
            data={'tbname':table, 'body':json.dumps(body)}
            ci.db.query("insert into tags(tbname,body) values('{tbname}','{body}')",data)
        else:
            old=json.loads(row['body'])
            for k in body.keys():
                old[k]=body[k]
            data={'body':json.dumps(old),'id':row['id']}
            ci.db.query("update tags set body='{body}' where id='{id}'",data)
        return 'success'

    def listtag(self,param=''):
        params=self._params(param)
        rows=ci.db.query("select tbname,body from tags")
        # return rows
        s=set()
        for row in rows:
            tags=json.loads(row['body'])
            for k in tags.keys():
                s.add('object_name: '+row['tbname'].encode('utf-8')+"\ttags: "+ k.encode('utf-8')+"=%s"% tags[k].encode('utf-8') )
        return "\n".join(s)


    def _check_body_val(self,table,key,value):
        row=ci.db.scalar("select body from tags where tbname='%s' limit 1 offset 0"%table)
        body={}
        if row!=None:
            body=json.loads(row['body'])
        else:
            return True,'OK'
        if key in body.keys():
            if body[key]!='':
                if value in body[key].split(','):
                    return  True,'OK'
                else:
                    return  False," value:'%s' must be in %s" %(key,str(body[key].encode('utf-8').split(',')))
            else:
                return True,'OK'
        else:
            return False," tag name must be in %s" %(str([ k.encode('utf-8') for k in body.keys()]))


################################################ hosts ###############################################

    def addhosttag(self,param=''):
        params=self._params(param)
        tag=''
        ip=''
        if 't' in params:
            tag=params['t']
        else:
            return '-t(tag) require'
        if tag.find('=')==-1:
            return 'tag must be "key=value"'
        if 'i' in params:
            ip=params['i']
        else:
            return '-i(ip) require'
        body={}
        for t in tag.split(';'):
            kv=t.split('=')
            if len(kv)==2:
                ok,messege=self._check_body_val('hosts',kv[0],kv[1])
                if not ok:
                    return messege.encode('utf-8')
                body[kv[0]]=kv[1]

        row=ci.db.scalar("select id,body from hosts where ip='{ip}' limit 1 offset 0",{'ip':ip})
        if row==None:
            data={'ip':ip,'body':json.dumps(body)}
            ci.db.query("insert into hosts(ip,body) values('{ip}','{body}')",data)
        else:
            old=json.loads(row['body'])
            for k in body.keys():
                old[k]=body[k]
            data={'ip':ip,'body':json.dumps(old),'id':row['id']}
            ci.db.query("update hosts set ip='{ip}',body='{body}' where id='{id}'",data)
        return 'success'
    # @cache.Cache(ttl=300)
    def gethost(self,param=''):
        params=self._params(param)
        if 't' not in params:
            return '-t(tag) require'
        rows=ci.db.query("select ip,body from hosts")
        # rows=self._cache_table('hosts')
        ret=[]
        tag=params['t']
        start=time.time()
        rows= self._search_body('hosts',tag)
        print(time.time()-start)
        for row in rows:
                # ret.append(row['ip'])
                ret.append(row['app'])
        return "\n".join(ret)

    def viewhost(self,param=''):
        params=self._params(param)
        if 'i' not in params:
            return '-i(ip) require'
        else:
            ip=params['i']
        data={'ip':ip}
        row=ci.db.scalar("select ip,body from hosts where ip='{ip}' limit 1 offset 0",data)
        return row['body']
    # @cache.Cache(ttl=3600)
    def listhosttag(self,param=''):
        params=self._params(param)
        rows=ci.db.query("select body from hosts")
        # return rows
        s=set()
        for row in rows:
            tags=json.loads(row['body'])
            for k in tags.keys():
                s.add(k.encode('utf-8')+"=%s"% tags[k].encode('utf-8') )
        return "\n".join(s)

    @cache.Cache(ttl=3600,key="#p[0]",md5=False)
    def _cache_table(self,table):
        print('xxxxxx')
        return ci.db.query("select * from %s" % table)


    def aaa(self,param=''):
        print ci.loader.helper('DictUtil')
        rows=ci.db.query('select * from hosts')
        print rows
        #return ci.loader.helper('DictUtil').query(rows,'select aa,bb,ip where ip like 172.17.140.133')
        return ci.loader.helper('DictUtil').query({"xx":"x"},"select aa,bb,ip where ip like '' ")

    def abc(self):
        s=time.time()
        for i in xrange(1,100000):
            self._cache_table('hosts')[0]
        print(time.time()-s)
        return 'abc'

    @CI_Cache.Cache(ttl=3600,key='#ip')
    def test2(self,id="id",ip='172.16.133.12',dd={'ip':'xxxxxxxxx'},xx=''):
        print 'xxxxxxxx'
        # start=time.time()
        # rows=self.db.query('select * from hosts limit 5')
        # print(time.time()-start)
        # start=time.time()
        # data=[]
        #
        #
        # for index,row in enumerate(rows):
        #     r=json.loads(row['body'])
        #
        #     rows[index]=r
        # return rows



    def test3(self,param=''):
        rows=self._cache_table('hosts')
        for index,row in enumerate(rows):
            r=json.loads(row['body'])

            rows[index]=r
        # import pymongo
        #
        # conn = pymongo.MongoClient("127.0.0.1",27017)
        # db = conn.test
        # for row in rows:
        #
        #     db.test.insert_one(row)



    def test(self,param=''):

        # from data_query_engine import DataQueryEngine

        rows=self._cache_table('hosts')
        # rows=self.db.query('select * from hosts limit 10')
        # rows=self.db.query('select * from hosts ')
        start=time.time()
        data=[]

        for index,row in enumerate(rows):
            r=json.loads(row['body'])

            rows[index]=r


        # print(rows)
        # query = DataQueryEngine(rows, "select * from ")
        # return  query.get_results()




        # query = Sql4Json(json.dumps({"data":rows}), "select ip,business from / where room_en_short=='GZ-NS'")
        # query = Sql4Json(json.dumps({"data":rows}), "select * from data")
        # query = Sql4Json(json.dumps(rows), "select ip,business from / where  module > 'sync-web'")


        # query = DataQueryEngine(rows, "select * from  /  where  module == 'sync-web'")
        # return  query.get_results()
        #
        # print time.time()-start
        # results_dictionary = query.get_results()
        # return results_dictionary







    def _search_body(self,table='', exp=''):
        # assert  table!=''
        # exp=exp.replace('&&',' and ')
        # exp=exp.replace('||',' or ')
        # rows=ci.db.query("select * from %s"%table)
        # ret=[]
        # def tmp(a):
        #     return ('('+(a.group(0)).encode("utf-8").replace("'",'')+')').decode('utf-8')
        # exp=re.sub(r'(\w+\s*(=|like)\s*[\'](?:[^\']+)[\'])|(\w+(=|like)\s*(?:[^\s]+)\s*)',tmp,exp)
        # print(exp)
        # s=time.time()
        rows=ci.db.query("select * from %s"%table)

        ret=[]

        # for row in rows:
        #     row['ip']=row['ip']



        rows=map(lambda row: json.loads( row['body']) ,rows)


        dutil=ci.loader.helper('DictUtil')

        print(rows)



        return  dutil.query( rows,select="name", where=exp)


        # expmatch= dutil.query( rows, exp)
        #
        # print len(rows)
        #
        #
        # ret = filter(lambda row: expmatch.calc(data_dict=json.loads( row['body'])), rows)
        # print("xxxxxxxxxxxxxx:"+str(time.time()-s))
        # return ret

# ################################################ objs ###############################################
    def addobjs(self,param=''):
            params=self._params(param)
            tag=''
            ip=''
            otype='hosts'
            key=''
            if 't' in params:
                tag=params['t']
            else:
                return '-t(tag) require'
            if tag.find('=')==-1:
                return 'tag must be "key=value"'
            if 'i' in params:
                ip=params['i']
            else:
                return '-i(ip) require'
            if 'o' in params:
                otype=params['o']
            else:
                return '-o(object type) require'
            if 'k' in params:
                key=params['k']
            else:
                key=ip
            body={}
            for t in tag.split(';'):
                kv=t.split('=')
                if len(kv)==2:
                    ok,messege=self._check_body_val(otype,kv[0],kv[1])
                    if not ok:
                        return messege.encode('utf-8')
                    body[kv[0]]=kv[1]

            row=ci.db.scalar("select id,body from objs where key='{key}' and otype='{otype}' limit 1 offset 0",{'key':key,'otype':otype})
            if row==None:
                body['_key']=key
                body['_otype']=otype
                data={'ip':ip,'body':json.dumps(body),'otype':otype,'key':key}
                ci.db.query("insert into objs(ip,body,otype,key) values('{ip}','{body}','{otype}','{key}')",data)
            else:
                old=json.loads(row['body'])
                for k in body.keys():
                    old[k]=body[k]
                data={'ip':ip,'body':json.dumps(old),'id':row['id']}
                ci.db.query("update objs set ip='{ip}',body='{body}' where id='{id}'",data)
            return 'success'

    def getobjs(self,param=''):
        params=self._params(param)
        otype=''
        tag=''
        cols='*'
        if 't' not in params:
            return '-t(tag) require'
        else:
            tag= params['t']
        if 'o' not in params:
            return '-o(object type) require'
        else:
            otype=params['o']
        if 'c'  in params:
            cols= params['c']
        rows=ci.db.query("select * from objs where otype='{otype}'",{'otype':otype})
        rows=map(lambda row:json.loads(row['body']),rows)
        print(rows)
        return ci.loader.helper('DictUtil').query(rows,select=cols,where=tag)

