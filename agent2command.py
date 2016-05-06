#! usr/bin/python
#coding=utf-8  

import sys,shutil,subprocess,time,traceback
import  os, atexit
from signal import SIGTERM
reload(sys)
sys.setdefaultencoding('utf-8')
from StringIO import StringIO
import Queue
import threading

import asyncore,asynchat,socket
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import cgi
import getopt
import uuid
import hashlib   


ToAgent = Queue.Queue(2000) ## list:[ (ZbxCommand)... ]
ToResponse = Queue.Queue(2000) ## list:[ (ZbxCommand)... ]
mapSock = {} 
mapUuid = {} ## key:uuid value : ZbxHttpHTTPRequest,create_timestamp

##配置开始
maxTime = 30 ##5秒超时
maxProcess = 500 ##命令进程池最大数量
pidfile = "/var/ZbxDaemon.pid" ##pid文件
authKey = "adfasdfjlajdfljdfslmeizu.comasdfasdf" ##authKEy 计算方法 md5(timestamp+authKEy)
authTime = 5 ##key过期时间为5秒
host ="0.0.0.0" ##监听IP
port = 8888 ##监听端口
##配置结束

try:
    
    opts, args = getopt.getopt(sys.argv[2:], '',["host=","dport=","maxProcess=","maxTime=","authKey=","authTime=","pidfile="])
    kvopts = dict(opts) 
    opt = kvopts.get('--host',None)
    if opt:
        host = opt
    opt = kvopts.get('--dport',None)
    if opt:
        port = int(opt)
    opt = kvopts.get('--maxProcess',None)
    if opt:
        maxProcess = int(opt)
    opt = kvopts.get('--maxTime',None)
    if opt:
        maxTime = int(opt)
    opt = kvopts.get('--authKey',None)
    if opt:
        authKey = opt
    opt = kvopts.get('--authTime',None)
    if opt:
        authTime = int(opt)
    opt = kvopts.get('--pidfile',None)
    if opt:
        pidfile = opt    
except getopt.GetoptError: 
    print "opts parse fail"
    sys.exit(0)


def pre_logger():
    import logging
    from logging.handlers import RotatingFileHandler
    import tempfile
    get_this_time =lambda : time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(time.time() ))
    client_log_filename=tempfile.gettempdir()+ os.path.sep +'Agent2Command.log'
    logger = logging.getLogger()
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-25s %(module)s:%(lineno)d  %(levelname)-8s %(message)s',
                    #datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=client_log_filename,
                    filemode='a')
    logger.addHandler(RotatingFileHandler(filename=client_log_filename,maxBytes=100 * 1024 * 1024, backupCount=3))
    logger = logger
    logger.info("[Agent2Command is begin %s]" %  get_this_time()  )
    return logger
logger = pre_logger()
class Daemon(object):
        """
        A generic daemon class.
       
        Usage: subclass the Daemon class and override the run() method
        """
        def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
                self.stdin = stdin
                self.stdout = stdout
                self.stderr = stderr
                self.pidfile = pidfile
       
        def daemonize(self):
                """
                do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                """
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit first parent
                                sys.exit(0)
                except OSError, e:
                        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
                        sys.exit(1)
       
                # decouple from parent environment
                os.chdir("/")
                os.setsid()
                os.umask(0)
       
                # do second fork
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit from second parent
                                sys.exit(0)
                except OSError, e:
                        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
                        sys.exit(1)
       
                # redirect standard file descriptors
                sys.stdout.flush()
                sys.stderr.flush()
                si = file(self.stdin, 'r')
                so = file(self.stdout, 'a+')
                se = file(self.stderr, 'a+', 0)
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())
       
                # write pidfile
                atexit.register(self.delpid)
                pid = str(os.getpid())
                file(self.pidfile,'w+').write("%s\n" % pid)
       
        def delpid(self):
                os.remove(self.pidfile)
 
        def start(self):
                """
                Start the daemon
                """
                # Check for a pidfile to see if the daemon already runs
                try:
                        pf = file(self.pidfile,'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None
                if pid:
                        message = "pidfile %s already exist. Daemon already running?\n"
                        sys.stderr.write(message % self.pidfile)
                        sys.exit(1)
               
                # Start the daemon
                self.daemonize()
                self.run()
 
        def stop(self):
                """
                Stop the daemon
                """
                # Get the pid from the pidfile
                try:
                        pf = file(self.pidfile,'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None
       
                if not pid:
                        message = "pidfile %s does not exist. Daemon not running?\n"
                        sys.stderr.write(message % self.pidfile)
                        return # not an error in a restart
 
                # Try killing the daemon process       
                try:
                        while 1:
                                os.kill(pid, SIGTERM)
                                time.sleep(0.1)
                except OSError, err:
                        err = str(err)
                        if err.find("No such process") > 0:
                                if os.path.exists(self.pidfile):
                                        os.remove(self.pidfile)
                        else:
                                print str(err)
                                sys.exit(1)
 
        def restart(self):
                """
                Restart the daemon
                """
                self.stop()
                self.start()

def PushTraceback():
    fstring = StringIO()
    traceback.print_exc(file=fstring)
    message = fstring.getvalue()
    print message
    return message

class ZbxCommand(object):
    def __init__(self):
        self.command = None
        self.ctime = 0
        self.uuid = None
        self.execobj = None
        self.status = 0 ##0未启动 1已启动 2已关闭
        self.stdout = ""
        self.stderr = ""

##受理连接
class ZbxHttpHTTPRequest(BaseHTTPRequestHandler,asynchat.async_chat):
    def __init__(self, sock,addr):
        self.addr  = addr
        self.ctime = time.time()
        asynchat.async_chat.__init__(self,sock,map=mapSock)
        self.uuid = "%s-%s" % (uuid.uuid1(),uuid.uuid4()) 
        mapUuid[self.uuid] = self
        self.iBuffer = []
        self.header_end= False
        self.set_terminator(1)

    def parse_headers(self):
        request_text = "".join(self.iBuffer)
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
        # print mapUuid
        # print self.headers.keys()
        # print self.command
        # print self.error_code
        # print self.path
        # print request_text

    def collect_incoming_data(self,data):
        self.iBuffer.append(data)

    def found_terminator(self):
        if self.header_end:
            self.parse_headers()
            self.parse_post()

        self.set_terminator(1)
        if "\r\n\r\n" == "".join(self.iBuffer[-4:]):
            logger.info("get http header : %s %s " % self.addr)
            self.parse_headers()
            if self.headers.has_key("Content-Length"):
                self.header_end = True
                self.set_terminator(int(self.headers["Content-Length"]))
            else:
                self.response_post("no found post data\npost data pattern: 'cli=[command]&__auth=[md5(now_timestamp+authKey)]&__timestamp=[int(now_timestamp)]'\n")

    ##解析POST信息,压入命令队列
    def parse_post(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        self.post = postvars
        logger.info("host:%spost info:%s" % (self.addr,postvars) )
        cli = self.post.get('cli')
        auth = self.post.get('__auth')
        timestamp = self.post.get('__timestamp')
        # if not auth or not timestamp:
        #     self.response_post("auth parameter and timestamp parameter must required\n")
        #     return
        # timestamp = "".join(timestamp)
        # auth = "".join(auth)
        # if self.ctime - int(timestamp) > authTime:
        #     self.response_post("auth timestamp is out of date\n")
        #     return 

        # m2 = hashlib.md5(timestamp+authKey)
        # if str(m2.hexdigest()) <> auth:
        #     self.response_post("auth failed!\n")
        #     return 
        if cli:
            try:
                zbxcli = ZbxCommand()
                zbxcli.ctime = self.ctime
                zbxcli.command = "".join(cli)
                logger.info("host:%scommon info:%s" % (self.addr,zbxcli.command) )
                zbxcli.uuid = self.uuid
                ToAgent.put( zbxcli,block=False )
            except Queue.Full,e:
                self.response_post("zbxcli agent queue is full,please wait time replay...\n")
            except BaseException,e:
                PushTraceback()
                self.response_post("zbxcli agent error ,please contact administrator...\n")
        else:
            self.response_post("cli parameter must required\n")


        
    ##回复POST
    def response_post(self,data):
        try:
            mapUuid.pop(self.uuid,None)
            http_response="""HTTP/1.1 200 OK\r\nServer: ZbxHttpServer\r\n\r\n%s""" % data
            self.send(http_response)
            self.close()
        except BaseException as e:

            logger.error("host:%s,uuid:%s,error send %s,error info :%s" %(self.addr,self.uuid , data,e) )
        



class ZbxHttpServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self,map=mapSock)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind( (host,port) )
        self.listen(1024)
        

    def handle_accept(self):
        try:
            sock,addr = self.accept()
            logger.info("Accept Request addr : %s %s" % addr)
            ZbxHttpHTTPRequest(sock,addr)
        except BaseException as e:
            logger.error(e)

class ZbxCliThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.iPorcess = {}


    ##从队列里面取出命令并执行
    def start_cli(self):
        for i in range(0,maxProcess -  len(self.iPorcess)):
            try:
                zbxcli = ToAgent.get(block=False)
                logger.info("get command :%s" % zbxcli.command)
                self.iPorcess[zbxcli.uuid] = zbxcli
            except Queue.Empty ,qe:
                time.sleep(0.005)
                break
        for zbxcli in [zbx for zbx in self.iPorcess.values() if zbx.status == 0]:
            zbxcli.execobj =  subprocess.Popen(zbxcli.command, stdout = subprocess.PIPE, stderr = subprocess.PIPE,shell=True)
            zbxcli.status = 1

    ##检测命令是否执行完成
    def poll_cli(self):
        now = time.time()
        for zbxcli in [zbx for zbx in self.iPorcess.values() if zbx.status == 1]:
            try:
                ##如果跑完了就回调
                if not zbxcli.execobj.poll() is None:
                    zbxcli.status = 2
                    zbxcli.stdout = zbxcli.execobj.stdout.read()
                    zbxcli.stderr = zbxcli.execobj.stderr.read()
                    try:
                        
                        ToResponse.put(zbxcli,block=False)
                        del self.iPorcess[zbxcli.uuid]
                        logger.info("success command :%s" % zbxcli.command)
                        continue
                    except Queue.Full:
                        logger.error("Queue Full,ToResponse:%s,ToAgent:%s" % (ToResponse.qsize(),ToAgent.qsize()) )
                    except BaseException as e:
                        logger.error("response exception:%s" % e)

                ##超时处理
                if now - zbxcli.ctime > maxTime:
                    zbxcli.execobj.kill()
                    logger.info("timeout  command :%s" % zbxcli.command)
                    del self.iPorcess[zbxcli.uuid]

            except BaseException,e:
                del self.iPorcess[zbxcli.uuid]
                logger.error(PushTraceback())
            

    def loop(self):
            try:

                self.start_cli()
                self.poll_cli()
            except BaseException,e :
                logger.error(PushTraceback())

    def run(self):
        while True:
            self.loop()

class ZbxDaemon(Daemon):
# class ZbxDaemon(object):
    ##回复HTTP请求
    def process_respond(self):
        try:
            zbxcli = ToResponse.get(block=False)
            logger.info("response command is %s" % zbxcli.command)
            handler = mapUuid.get(zbxcli.uuid,None)
            if handler:
                message = [zbxcli.stdout]
                if zbxcli.stderr:
                    message += ["error:%s\n" % zbxcli.stderr]
                message = "\n".join(message)
                handler.response_post(message)
        except Queue.Empty ,qe:
            pass

    ##超时处理
    def recycle_map(self):
        try:
            now = time.time()
            for uuid in mapUuid.keys():
                handler = mapUuid[uuid]
                if now - handler.ctime > maxTime:
                    logger.info("recycle uuid : %s" % uuid)
                    try:
                        handler.response_post("zbxcli agent queue is time out\n")
                    except BaseException as e:
                        logger.error(e)
                           
        except BaseException as  e:
            logger.error(e)

    def run(self):
        http =ZbxHttpServer(host,port)
        cliagent = ZbxCliThread()
        cliagent.start()
        while True:
            try:
                asyncore.loop(count = 1,timeout=0.5,use_poll = True,map = mapSock)

                self.recycle_map()
                self.process_respond()
            except KeyboardInterrupt,e:
                http.close()
                sys.exit(0)
            except BaseException,e :
                logger.error(PushTraceback())

def DeamonMain():
    daemon = ZbxDaemon(pidfile)
    
    if len(sys.argv) >= 2:
            opt = sys.argv[1]
            if 'start' == opt:
                    daemon.start()
            elif 'stop' == opt:
                    daemon.stop()
            elif 'restart' == opt:
                    daemon.restart()
            else:
                    print "Unknown command"
                    sys.exit(2)
            sys.exit(0)
    else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            print "or usage: %s start|stop|restart --host [host] --dport [port] --maxProcess [maxProcess]" % sys.argv[0]
            sys.exit(2)


if __name__ == "__main__":
    DeamonMain()
    # p = ZbxDaemon()
    # p.run()
    



