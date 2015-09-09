#!/usr/bin/python
# -*- coding:utf8 -*-
__author__ = 'xiaozhang'

import os
import urllib2
import urllib
import subprocess
import time
import datetime
import re
import logging
import sys
import json
import tempfile
import threading
import getopt



server_url="http://127.0.0.1:8005/zbxcli"

bin_name='client'
client_filename='/bin/%s' % bin_name
client_log_filename= tempfile.gettempdir()+os.path.sep+ bin_name+".log"
client_script_path= tempfile.gettempdir()+ os.path.sep+'script'









logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)-25s %(module)s:%(lineno)d  %(levelname)-8s %(message)s',
                #datefmt='%a, %d %b %Y %H:%M:%S',
                filename=client_log_filename,
                filemode='a')





class ClientCommand(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.uuid=str(datetime.datetime.now()).replace(' ','').replace(':','').replace('-','').replace('.','')
        self.result=open(tempfile.gettempdir()+ os.path.sep +self.uuid,'a+')

    def run(self, timeout=10):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True,stdout=self.result,stderr=self.result)
            self.process.communicate()
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            logger.info(self.cmd)
            #print 'Terminating process'
            self.process.terminate()
            thread.join()
            util=ClientUtil()
            util.url_fetch(server_url+'/slowlog',{'param':{ 'cmd':self.cmd,'ip':util.get_one_ip()}})
            return "13800138000"
        result= open(tempfile.gettempdir()+ os.path.sep+self.uuid,'r').read()
        os.unlink(tempfile.gettempdir()+ os.path.sep+self.uuid)
        return result


class ClientUtil(object):
    def urlencode(self,str):
        reprStr=repr(str).replace(r'\x','%')
        return reprStr[1:-1]

    def download(self,filename):
        data={'file':filename}
        data=urllib.urlencode(data)
        http_url='http://%s/Index/download?%s' % (server_url,data)
        conn = urllib2.urlopen(http_url)
        f = open(filename,'wb')
        f.write(conn.read())
        f.close()

    def upload(self,filepath):
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        fr=open(filepath,'rb')
        filename=os.path.basename(filepath)
        data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % ('file',filename))
        data.append('Content-Type: %s\r\n' % 'image/png')
        data.append(fr.read())
        fr.close()
        data.append('--%s--\r\n' % boundary)


        http_url='http://%s/Index/upload' % server_url
        # http_url='http://172.16.136.98:8005/Index/index'
        http_body='\r\n'.join(data)
        try:
            req=urllib2.Request(http_url, data=http_body)
            req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
            req.add_header('User-Agent','Mozilla/5.0')
            req.add_header('Referer','http://remotserver.com/')
            resp = urllib2.urlopen(req, timeout=5)
            qrcont=resp.read()
            print qrcont
        except Exception,e:
            print 'http error'

    def url_fetch(self,url,data=None,timeout=4):
        html='';
        # print(url)
        try:
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
            }
            if data!=None:
                data=urllib.urlencode(data)
            req = urllib2.Request(
                url =url,
                headers = headers,
                data=data
            )
            html=urllib2.urlopen(req,timeout=timeout).read()
            charset=re.compile(r'<meta[^>]*charset=[\'\"]*?([a-z0-8\-]+)[\'\"]?[^>]*?>',re.IGNORECASE).findall(html)
            if len(charset) >0:
                if charset[0]=='gb2312':
                    charset[0]='gbk'
                html=unicode(html,charset[0])
            #print(html)
        except Exception as e:
            logger.error(e)
        return html


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



    def now_datetime(self):
        now_datetime = time.strftime('_%Y-%m-%d_%H_%M_%S', time.localtime(time.time()))
        return now_datetime

    def backup_config(self,src):
        ret = 1
        if not os.path.exists(src):
            print 'not exist {0}'.format(src)
            logging.error("not exists {0}".format(src))
            sys.exit(-1)

        dst = ''.join([src, self.now_datetime()])
        if not os.path.exists(dst):
            ret = os.system('cp -af {0} {1}'.format(src, dst))
            if not ret:
                logging.info("cp -af {0} {1}".format(src, dst))
            else:
                print "cp error"
                logging.error("ret={0} cp {2} {2}".format(ret, src, dst))
                sys.exit(-2)
        else:
            print 'exist dst'
            logging.error("exist {0}".format(dst))
            sys.exit(-3)

        return ret

    def execute(self,cmd):
        try:
            return os.popen(cmd).read()
        except Exception as err:
            logger.error(err)
            return ""


    def get_all_ip_list(self):
        cmdline = "ip a | egrep \"^\s*inet.*\" | grep -v inet6 | awk '{print $2}' | awk -v FS='/' '{print $1}'"
        ret = self.execute(cmdline)
        lip=re.split(r'\n',ret)
        ips=[]
        for ip in lip:
            if str(ip).strip ()!='':
              ips.append(ip.strip())
        return ips


    def get_one_ip(self):
        ret = [x for x in self.get_all_ip_list() if x.startswith('10') or x.startswith('172') or x.startswith('192')]
        if len(ret)>1:
            return ret[0]
        return ''.join(ret)

    def get_hostname(self):
        os_name = os.name
        host_name = None
        if os_name == 'nt':
            host_name = os.getenv('computername')
        elif os_name == 'posix':
            host = os.popen('hostname')
            try:
                host_name = host.read().strip()
            finally:
                host.close()
        return host_name


    def exec_filename(self):
        import os, sys, inspect
        path = os.path.realpath(sys.path[0])
        if os.path.isfile(path):
            path = os.path.dirname(path)
            return os.path.abspath(path)+ os.path.sep+__file__
        else:
            caller_file = inspect.stack()[1][1]
            return os.path.abspath(os.path.dirname(caller_file))+ os.path.sep+__file__


    def backup_config(self,src):
        """

        :return:
        """
        ret = 1
        if not os.path.exists(src):
            print 'not exist {0}'.format(src)
            logging.error("not exists {0}".format(src))
            sys.exit(-1)

        dst = ''.join([src, self.now_datetime()])
        if not os.path.exists(dst):
            ret = os.system('cp -af {0} {1}'.format(src, dst))
            if not ret:
                logging.info("cp -af {0} {1}".format(src, dst))
            else:
                print "cp error"
                logging.error("ret={0} cp {2} {2}".format(ret, src, dst))
                sys.exit(-2)
        else:
            print 'exist dst'
            logging.error("exist {0}".format(dst))
            sys.exit(-3)

        return ret

    def update_config(self,src):
        """

        :return:
        """
        dst = '/data/zabbix/conf/zabbix_agentd.conf'
        ret = os.system('echo "{0}" > {1}'.format(src, dst))
        if not ret:
            logging.info("update {0}".format(dst))
        else:
            print "cp error"
            logging.error("ret={0} update {1} {2}".format(ret, src, dst))
            sys.exit(-2)

    def tuple2list(self,*args):
        print(args)
        l=[]
        for i in args:
            l.append(i)
        return l

    def command_args(self,args):
        if isinstance(args,list) or isinstance(args,tuple):
            return '"%s"' % '" "'.join(args)
        else:
            return str(args)

class Client():
    def __init__(self):
        self.entry=server_url+"/%s"
        self.util=ClientUtil()


    def upgrade(self,args):
        pass
        fn=self.util.exec_filename()
        open(client_filename,'w').write(self.util.url_fetch(self.entry%'upgrade'))

    def restart(self,args):
        pass


    def stop(self,args):
        pass

    def start(self,args):
        pass


    def default(self,cmd,args):
        argv= self.util.parse_argv(args)
        ret=self.util.url_fetch(self.entry%cmd,{'param':json.dumps(argv)})
        print(ret)

    def shell(self,args):
        if len(args)<1:
            print('ERROR: param is not enough')
            sys.exit(0)

        path=client_script_path
        if not os.path.exists(path):
            os.mkdir(path)
        fn=path+os.path.sep+args[0]
        src=''
        is_python=False
        result=-1
        if not os.path.exists(fn) or os.stat(fn).st_mtime<(time.time()-10*60):
            src=self.util.url_fetch(self.entry%'shell',{ 'key':args[0], 'param': json.dumps(args[1:])})
        if src!='':
            open(fn,'w').write(src)
        else:
            src=open(fn,'r').read()

        lines=re.split(r'\n',src)
        for line in lines:
            if line.strip()!='':
                break;
        if line.index('python')>0:
                is_python=True
        if is_python:
            cmd=ClientCommand('/usr/bin/python %s %s'% (fn,self.util.command_args(args[1:])))
            result=cmd.run(10)
        else:
            cmd=ClientCommand('/bin/bash %s %s'% (fn,self.util.command_args(args[1:])))
            result=cmd.run(10)
        print(result)

if __name__ == '__main__':
    cli=Client()
    util=ClientUtil()
    if len(sys.argv)<2:
        cli.default('help',['help'])
    else:
        cmd=sys.argv[1]
        if hasattr(cli,cmd):
           getattr(cli,cmd)(sys.argv[2:])
        else:
           cli.default(cmd,sys.argv[2:])







