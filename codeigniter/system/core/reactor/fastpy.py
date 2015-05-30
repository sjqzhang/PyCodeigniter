#!/usr/bin/python
#-*- coding:utf-8 -*-

import socket, logging
import select, errno
import os
import sys
import traceback
import gzip
from StringIO import StringIO
import Queue
import threading
import time
import thread
import cgi
from cgi import parse_qs
import json
import imp
from os.path import join, getsize
from urllib import unquote
import re
import platform



if 'epoll' in select.__dict__:
    print "use epoll"
    use_mod = 'epoll'
    from epollreactor import EpollReactor as Reactor
elif 'kqueue' in select.__dict__:
    print "use kqueue"
    use_mod = 'kqueue'
    from kqueuereactor import KqueueReactor as Reactor
elif 'poll' in select.__dict__:
    print "use poll"
    use_mod = 'poll'
    from pollreactor import PollReactor as Reactor
elif 'select' in select.__dict__:
    print "use select"
    use_mod = 'select'
    from selectreactor import SelectReactor as Reactor
else:
    print "There is no reactor can be used."


CI={'static_dir':'','app':None,'logger':None,'router':None}

from multiprocessing import cpu_count

##################user config ##################
logger = logging.getLogger()
static_file_dir = "static"
thread_count = 2*cpu_count() + 1
MaxReadSize = 1024*1024*1024
#############################################





static_dir = "/%s/" % static_file_dir
read_cache_dir = "read_cache"
cache_static_dir = "cache_%s" % static_file_dir
if not os.path.exists(cache_static_dir):
    pass
    # os.makedirs(cache_static_dir)
if not os.path.exists(read_cache_dir):
    pass
    # os.makedirs(read_cache_dir)
gzipdic = {"HTM":"text/html",
        "HTML":"text/html",
        "CSS":"text/css",
        "JS":"text/javascript",
        "TXT":"text/plain",
        "XML":"text/xml"}

mimedic = {"HTM":"text/html",
        "HTML":"text/html",
        "CSS":"text/css",
        "JS":"text/javascript",
        "TXT":"text/plain",
        "XML":"text/xml",
        "APK":"application/vnd.android.package-archive",
        "PXL":"application/iphone",
        "IPA":"application/iphone",
        "LUA":"application/force-download"}

def getTraceStackMsg():
    tb = sys.exc_info()[2]
    msg = ''
    for i in traceback.format_tb(tb):
        msg += i
    return msg

#action_dic = {}
action_time = {}
listfile = os.listdir("./")
for l in listfile:
    if l == str(__file__):
        continue
    prefixname, extname = os.path.splitext(l)
    if extname == ".py":
        try:
            __import__(prefixname)
        except Exception as e:
            # CI['logger'].error(e)
            continue
        mtime = os.path.getmtime(l)
        action_time[prefixname] = mtime
        #action_dic[prefixname] = action

class FeimatLog():
    def __init__(self, filename):
        logtime = time.strftime(".%Y-%m-%d")
        self.curlogname = filename + logtime
        self.f = open(self.curlogname, "a")
        self.basename = filename

    def __del__(self):
        self.f.close()

    def log(self, msg):
        curlogtime = time.strftime(".%Y-%m-%d")
        detaillogtime = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        curlogname = self.basename + curlogtime
        if curlogname != self.curlogname:
            self.f.close()
            self.curlogname = curlogname
            self.f = open(self.curlogname, "a")
        self.f.write(detaillogtime + msg+"\n")
        self.f.flush()
        pass

def myparse_qs(input, d):
    p_list = input.split("&")
    for sub in p_list:
        if sub == None or sub == "" or \
                "=" not in sub:
            continue
        sub = unquote(sub)
        v_list = sub.split("=")
        k = v_list[0]
        v = v_list[1]
        d[str(k)] = str(v)

class QuickHTTPRequest():
    def __init__(self, res_headers,aclog,data,ev_fd,fd):
        self.res_headers = res_headers
        self.aclog = aclog
        self.data = data
        self.ev_fd = ev_fd
        self.fd = fd

    def ret(self,res):
        add_head = ""
        try:
            if res == None:
                return None
            if self.res_headers.get("Content-Encoding","") == "gzip":
                buf = StringIO()
                f = gzip.GzipFile(mode='wb', fileobj=buf)
                f.write(res)
                f.close()
                res = buf.getvalue()
            self.aclog.log(" success: %s" % (self.path))
        except Exception as e:
            CI['logger'].error(e)
            self.aclog.log(" fail: %s %s" % (self.path, str(e)+getTraceStackMsg()))
            res = "404 Not Found"
        try:
            if self.res_headers.get("Connection","") != "close":
                self.data["keepalive"] = True
            res_len = len(res)
            self.res_headers["Content-Length"] = res_len
            for key in self.res_headers:
                add_head += "%s: %s\r\n" % (key, self.res_headers[key])
            if res == "404 Not Found":
                self.data["writedata"] = "HTTP/1.1 404 Not Found\r\n%s\r\n%s" % (add_head, res)
            else:
                self.data["writedata"] = "HTTP/1.1 200 OK\r\n%s\r\n%s" % (add_head, res)
            if "read_cache_name" in self.data:
                os.remove(self.data["read_cache_name"])
                del self.data["read_cache_name"]
            self.ev_fd.modify(self.fd, self.ev_fd.EV_OUT | self.ev_fd.EV_IN | self.ev_fd.EV_DISCONNECTED)
        except Exception as e:
            CI['logger'].error(e)
            pass


    def parse(self, param):
        self.client_ip = param["addr"][0]
        self.client_port = param["addr"][1]
        if "rc" in param:
            fp = param["rc"]
            data = ""
            while True:
                subdata = fp.read(1024)
                if subdata == "":
                    break
                data += subdata
                headend = data.find("\r\n\r\n")
                if headend > 0:
                    break
            fp.seek(0)
        else:
            data = param["toprocess"]
            headend = data.find("\r\n\r\n")
            fp = StringIO(data)
        if headend > 0:
            headlist = data[0:headend].split("\r\n")
        else:
            headlist = data.split("\r\n")
        first_line = headlist.pop(0)
        self.command, self.path, self.http_version, =  re.split('\s+', first_line)
        indexlist = self.path.split('?')
        self.baseuri = indexlist[0]
        indexlist = self.baseuri.split('/')
        while len(indexlist) != 0:
            self.index = indexlist.pop()
            if self.index == "":
                continue
            else:
                self.action,self.method = os.path.splitext(self.index)
                self.method = self.method.replace('.', '')
                break
        self.headers = {}
        for item in headlist:
            if item.strip() == "":
                continue
            segindex = item.find(":")
            if segindex < 0:
                continue
            key = item[0:segindex].strip()
            value = item[segindex+1:].strip()
            self.headers[key.lower()] = value

        self.command = self.command.lower()
        self.getdic = {}
        self.form = {}
        self.filedic = {}
        self.body = ""
        if self.command  == "get" and "?" in self.path:
            myparse_qs(self.path.split("?").pop(), self.getdic)
            #for key in self.getdic:
            #    self.getdic[key] = self.getdic[key][0]
        elif self.command == "post" and self.headers.get('content-type',"").find("boundary") > 0:
            cgiform = cgi.FieldStorage(fp=fp,headers=None,
                    environ={'REQUEST_METHOD':self.command,'CONTENT_TYPE':self.headers['content-type'],})
            for key in cgiform:
                fileitem = cgiform[key]
                if fileitem.filename == None:
                    self.form[key] = fileitem.file.read()
                else:
                    self.filedic[key] = fileitem
        elif self.command == "post":
            self.body = data[headend+4:]
            myparse_qs(self.body, self.form)
            #for key in self.form:
            #    self.form[key] = self.form[key][0]
        if "rc" in param:
            param["rc"].close()
            del param["rc"]

def sendfilejob(aclog, request, data, ev_fd, fd):
    try:
        base_filename = request.baseuri[request.baseuri.find(static_dir):]
        cache_filename = "./cache_"+base_filename
        filename = "./"+base_filename
        return_content_type = None
        if not os.path.exists(filename) or ".." in base_filename:
            res = "404 Not Found"
            data["writedata"] = "HTTP/1.1 404 Not Found\r\nContent-Length: %s\r\nConnection:keep-alive\r\n\r\n%s" % (len(res),res)
            aclog.log(" fail: %s not found" % (request.path))
        else:
            lasttimestr = request.headers.get("if-modified-since", None)
            filemd5 = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            timestr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(filemd5))
            curtime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))
            sock = data["connections"]
            if lasttimestr == timestr and "range" not in request.headers:
                data["writedata"] = "HTTP/1.1 304 Not Modified\r\nLast-Modified: %s\r\nETag: \"%s\"\r\nDate: %s\r\nConnection:keep-alive\r\n\r\n" % (timestr,filemd5,curtime)
            else:
                ext = request.method
                iszip = False
                Accept_Encoding = request.headers.get("accept-encoding", "")
                ext_upper = ext.upper()
                return_content_type = mimedic.get(ext_upper, None)
                if ext_upper in gzipdic or \
                        (ext == "" and "gzip" in Accept_Encoding and os.path.getsize(filename) < 1024*1024*5):
                    need_zip = False
                    if not os.path.exists(cache_filename):
                        need_zip = True
                    else:
                        cache_mtime = os.path.getmtime(cache_filename)
                        if cache_mtime < ctime or cache_mtime < filemd5:
                            need_zip = True
                    if need_zip:
                        d,f = os.path.split(cache_filename)
                        try:
                            if not os.path.exists(d):
                                os.makedirs(d)
                            f_out = gzip.open(cache_filename, 'wb')
                            f_out.write(open(filename,'rb').read())
                            f_out.close()
                        except Exception as e:
                            CI['logger'].error(e)
                            pass

                            # pass
                    filename = cache_filename
                    iszip = True


                filesize = os.path.getsize(filename)
                if "range" in request.headers:
                    range_value = request.headers["range"].strip(' \r\n')
                    range_value = range_value.replace("bytes=", "")
                    start,end = range_value.split('-')
                    if end == '':
                        end = filesize - 1
                    start = int(start)
                    end = int(end)
                    headstr = "HTTP/1.1 206 Partial Content\r\nLast-Modified: %s\r\nETag: \"%s\"\r\nDate: %s\r\n" % (timestr,filemd5,curtime)
                    headstr += "Accept-Ranges: bytes\r\nContent-Range: bytes %s-%s/%s\r\n" % (start,end,filesize)
                else:
                    start = 0
                    end = filesize - 1
                    headstr = "HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nLast-Modified: %s\r\nETag: \"%s\"\r\nDate: %s\r\n" % (timestr,filemd5,curtime)
                    if return_content_type != None:
                        headstr += "Content-Type: %s\r\n" % return_content_type
                offset = start
                totalsenlen = end - start + 1
                if totalsenlen < 0:
                    totalsenlen = 0
                if iszip:
                    headstr += "Content-Encoding: gzip\r\n"
                headstr += "Content-Length: %s\r\nConnection:keep-alive\r\n" % totalsenlen
                headstr += "\r\n"
                f = open(filename, 'rb')
                f.seek(offset)
                readlen = 102400
                if readlen > totalsenlen:
                    readlen = totalsenlen
                firstdata = f.read(readlen)
                headstr += firstdata
                totalsenlen -= len(firstdata)
                data["f"] = f
                data["totalsenlen"] = totalsenlen
                data["writedata"] = headstr
            aclog.log(" success: %s" % (request.path))
    except Exception, e:
        aclog.log(" fail: %s %s" % (request.path, str(e)+getTraceStackMsg()))
        res = "404 Not Found"
        data["writedata"] = "HTTP/1.1 404 Not Found\r\nContent-Length: %s\r\nConnection:keep-alive\r\n\r\n%s" % (len(res),res)
        pass
    try:
        ev_fd.modify(fd, ev_fd.EV_OUT | ev_fd.EV_IN | ev_fd.EV_DISCONNECTED)
    except Exception as e:
        CI['logger'].error(e)


class Worker(object):

    def __init__(self):
        self._obj_dict = {}
        self._mtime_dict = {}
        self.log = FeimatLog("access.log")

        # for l in listfile:
        #     if l == str(__file__):
        #         continue
        #     key, extname = os.path.splitext(l)
        #     if extname == ".py" and key in sys.modules:
        #         try:
        #             action = sys.modules[key]
        #             self._obj_dict[key] = eval("action.%s()" % key)
        #         except Exception as e:
        #             CI['logger'].error(e)
        #             continue
        #         self._mtime_dict[key] = action_time[key]

    # def getGloalAction(self, action_key):
    #     action = sys.modules.get(action_key, None)
    #     auto_update = False
    #     if action == None:
    #         auto_update = True
    #     else:
    #         try:
    #             auto_update = action.FastpyAutoUpdate
    #         except Exception, e:
    #             pass
    #     if not auto_update:
    #         return auto_update,None,None
    #     if action == None:
    #         action = __import__(action_key)
    #         mtime = os.path.getmtime("./%s.py" % action_key)
    #         action_time[action_key] = mtime
    #     else:
    #         load_time = action_time[action_key]
    #         mtime = os.path.getmtime("./%s.py" % action_key)
    #         if mtime>load_time:
    #             try:
    #                 del sys.modules[action_key]
    #                 del action
    #             except Exception, e:
    #                 pass
    #             action = __import__(action_key)
    #             action_time[action_key] = mtime
    #     return auto_update,action,mtime

    def process(self, data, ev_fd, fd):
        res = ""
        add_head = ""
        headers = {}
        is_authorized=True
        try:
            request = QuickHTTPRequest(headers,self.log,data,ev_fd,fd)
            request.parse(data)
            if CI['app'].server.pre_route_callback!=None:
                # print(request.getdic)
                if not CI['app'].server.pre_route_callback(request):
                    is_authorized=False
                    code="403 Forbidden"
                    res="403 Forbidden"

        except Exception as e:
            CI['logger'].error(e)

        try:
            headers["Content-Type"] = "text/html;charset=utf-8"
            headers["Connection"] = "keep-alive"
            if request.baseuri == "/favicon.ico":
                request.baseuri = "/"+static_file_dir+request.baseuri
            if static_dir in request.baseuri or "favicon.ico" in request.baseuri:
                sendfilejob(self.log,request,data,ev_fd,fd)
                return None
            # action_key = request.action
            # obj = self._obj_dict.get(action_key, None)
            # load_time = self._mtime_dict.get(action_key, None)
            # auto_update,action,mtime = self.getGloalAction(action_key)
            # if auto_update and (obj == None or load_time == None or mtime>load_time):
            #     self._mtime_dict[action_key] = mtime
            #     obj = eval("action.%s()" % action_key)
            #     self._obj_dict[action_key] = obj

            # method = getattr(obj, request.method)
            code="500 Internal server error"
            ctrl=request.baseuri.split(r'/')

            if len(ctrl)==3 and is_authorized:
                code,res=CI['router'].route(ctrl[1],ctrl[2],request.getdic)
                if not isinstance(res,str) and not isinstance(res,unicode):
                    res=str(json.dumps(res))

                else:
                    res=str(unicode(res).encode('utf-8'))


            # res = method(request, headers)
            if res == None:
                return None
            if headers.get("Content-Encoding","") == "gzip":
                buf = StringIO()
                f = gzip.GzipFile(mode='wb', fileobj=buf)
                f.write(res)
                f.close()
                res = buf.getvalue()
            self.log.log(" success: %s" % (request.path))
        except Exception, e:
            CI['logger'].error(e)
            # self.log.log(" fail: %s %s" % (request.path, str(e)+getTraceStackMsg()))
            res = "404 Not Found"
        try:
            if headers.get("Connection","") != "close":
                data["keepalive"] = True
            res_len = len(res)
            headers["Content-Length"] = res_len
            for key in headers:
                add_head += "%s: %s\r\n" % (key, headers[key])
            if code == "404 Not Found":
                data["writedata"] = "HTTP/1.1 404 Not Found\r\n%s\r\n%s" % (add_head, res)
            elif code=="500 Internal server error":
                data["writedata"] = "HTTP/1.1 500 Internal server error\r\n%s\r\n%s" % (add_head, res)
            else:
                data["writedata"] = "HTTP/1.1 200 OK\r\n%s\r\n%s" % (add_head, res)
            if "read_cache_name" in data:
                os.remove(data["read_cache_name"])
                del data["read_cache_name"]
            ev_fd.modify(fd, ev_fd.EV_OUT | ev_fd.EV_IN | ev_fd.EV_DISCONNECTED)
        except Exception as e:
            CI['logger'].error(e)
            pass



def InitLog():
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("network-server.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)


class MyThread(threading.Thread):
    ind = 0
    def __init__(self, threadCondition, shareObject, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.threadCondition = threadCondition
        self.shareObject = shareObject
        self.setDaemon(True)
        self.worker = Worker()


    def processer(self, param, ev_fd, fd):
        try:
            self.worker.process(param, ev_fd, fd)
        except Exception as er:
            CI['logger'].error(er)



    def run(self):
        while True:
            try:
                param, ev_fd, fd = self.shareObject.get()
                self.processer(param, ev_fd, fd)
            except Queue.Empty:
                continue
            except Exception as  er :
                 CI['logger'].error(er)


class ThreadPool:
    def __init__( self, num_of_threads=10):
        self.threadCondition=threading.Condition()
        self.shareObject=Queue.Queue()
        self.threads = []
        self.__createThreadPool( num_of_threads )


    def __createThreadPool( self, num_of_threads ):
        for i in range( num_of_threads ):
            thread = MyThread( self.threadCondition, self.shareObject)
            self.threads.append(thread)


    def start(self):
        for thread in self.threads:
            thread.start()


    def add_job( self, param, ev_fd, fd ):
        self.shareObject.put( (param, ev_fd, fd) )

def check_next_http(param, tp, ev_fd, fd, work):
    datas = param.get("readdata", "")
    if "" == datas:
        param["toprocess"] = ""
        return 0
    read_len = len(datas)
    contentlen = param.get("contentlen", -1)
    headlen = param.get("headlen", -1)
    if contentlen == -1:
        len_s = datas.find("Content-Length:")
        if len_s < 0:
            len_s = datas.lower().find("content-length:")
        if len_s > 0:
            len_e = datas.find("\r\n", len_s)
        if len_s > 0 and len_e > 0 and len_e > len_s+15:
            len_str = datas[len_s+15:len_e].strip()
            if len_str.isdigit():
                contentlen = int(datas[len_s+15:len_e].strip())
                param["contentlen"] = contentlen
    if headlen == -1:
        headend = datas.find("\r\n\r\n")
        if headend > 0:
            headlen = headend + 4
            param["headlen"] = headlen
    if (contentlen >= 0 and headlen > 0 and (contentlen + headlen) <= read_len) or \
           (contentlen == -1 and headlen > 0 and headlen <= read_len):
        one_http_len = headlen
        if contentlen > 0:
            one_http_len += contentlen
        param["toprocess"] = param["readdata"][0:one_http_len]
        param["readdata"] = param["readdata"][one_http_len:read_len]
        read_len = read_len - one_http_len
        param["contentlen"] = -1
        param["headlen"] = -1
        param["read_len"] = read_len
        tp.add_job(param,ev_fd,fd)
        #work.process(param,ev_fd,fd)
        return one_http_len
    else:
        param["toprocess"] = ""
        return 0

def clearfd(ev_fd, params, fd):
    try:
        ev_fd.unregister(fd)
    except Exception as e:
        CI['logger'].error(e)
        pass

    try:
        param = params[fd]
        param["connections"].close()
        f = param.get("f", None)
        if f != None:
            f.close()
        rc = param.get("rc", None)
        if rc != None:
            rc.close()
        if "read_cache_name" in param:
            os.remove(param["read_cache_name"])
    except Exception as  e:
        CI['logger'].error(e)
        pass

    try:
        del params[fd]
        #logger.error(getTraceStackMsg())
        #logger.error("clear fd:%s" % fd)
    except Exception as e:
        CI['logger'].error(e)
        pass

def run_main(listen_fd):
    try:
        ev_fd = Reactor()
        ev_fd.register(listen_fd.fileno(), ev_fd.EV_IN | ev_fd.EV_DISCONNECTED)
    except select.error, msg:
        logger.error(msg)


    tp = ThreadPool(thread_count)
    tp.start()
    work = Worker()
    pid = os.getpid()

    params = {}


    last_min_time = -1
    while True:
        try:
            ev_list = ev_fd.poll(1)
        except Exception, e:
            continue

        cur_time = time.time()
        for fd, events in ev_list:
            if fd == listen_fd.fileno():
                while True:
                    try:
                        conn, addr = listen_fd.accept()
                        conn.setblocking(0)
                        ev_fd.register(conn.fileno(), ev_fd.EV_IN | ev_fd.EV_DISCONNECTED)
                        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        #conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
                        params[conn.fileno()] = {"addr":addr,"writelen":0, "connections":conn, "time":cur_time}
                    except socket.error, msg:
                        break
            elif ev_fd.EV_IN & events:
                param = params.get(fd,None)
                if param == None:
                    continue
                param["time"] = cur_time
                datas = param.get("readdata","")
                cur_sock = params[fd]["connections"]
                read_len = param.get("read_len", 0)
                while True:
                    try:
                        data = cur_sock.recv(102400)
                        if len(data) == 0:
                            clearfd(ev_fd,params,fd)
                            break
                        else:
                            datas += data
                            read_len += len(data)
                    except socket.error, msg:
                        if msg.errno == errno.EAGAIN or msg.errno == 10035:
                            param["read_len"] = read_len
                            len_s = -1
                            len_e = -1
                            contentlen = param.get("contentlen", -1)
                            headlen = param.get("headlen", -1)
                            if contentlen == -1:
                                len_s = datas.find("Content-Length:")
                                if len_s < 0:
                                    len_s = datas.lower().find("content-length:")
                                if len_s > 0:
                                    len_e = datas.find("\r\n", len_s)
                                if len_s > 0 and len_e > 0 and len_e > len_s+15:
                                    len_str = datas[len_s+15:len_e].strip()
                                    if len_str.isdigit():
                                        contentlen = int(datas[len_s+15:len_e].strip())
                                        param["contentlen"] = contentlen
                            if contentlen > MaxReadSize:
                                clearfd(ev_fd,params,fd)
                                break
                            if headlen == -1:
                                headend = datas.find("\r\n\r\n")
                                if headend > 0:
                                    headlen = headend + 4
                                    param["headlen"] = headlen
                            if ": multipart/form-data; boundary" in datas and \
                               len(datas) > 1024*1024*3 and "rc" not in param:
                                if headlen > 0 and contentlen > 0:
                                    param["rc"] = open("%s/%s_%s.tmp" % (read_cache_dir,pid,fd), "wb")
                                    pass
                                else:
                                    clearfd(ev_fd,params,fd)
                                    break
                            if "rc" in param:
                                param["rc"].write(datas)
                                param["readdata"] = ""
                            else:
                                param["readdata"] = datas
                            toprocess = param.get("toprocess", "")
                            if "" == toprocess and \
                                    ((contentlen >= 0 and headlen > 0 and (contentlen + headlen) <= read_len) or \
                                    (contentlen == -1 and headlen > 0 and headlen <= read_len)):
                                if "rc" in param:
                                    param["rc"].close()
                                    param["read_cache_name"] = "%s/%s_%s.tmp" % (read_cache_dir,pid,fd)
                                    param["rc"] = open(param["read_cache_name"], "rb")
                                    read_len = 0
                                else:
                                    one_http_len = headlen
                                    if contentlen > 0:
                                        one_http_len += contentlen
                                    param["toprocess"] = param["readdata"][0:one_http_len]
                                    param["readdata"] = param["readdata"][one_http_len:]
                                    read_len = read_len - one_http_len
                                    #logger.error(json.dumps(param["addr"])+param["toprocess"])
                                param["contentlen"] = -1
                                param["headlen"] = -1
                                param["read_len"] = read_len
                                tp.add_job(param,ev_fd,fd)
                                #work.process(param,ev_fd,fd)
                            break
                        else:
                            clearfd(ev_fd,params,fd)
                            break
            elif ev_fd.EV_DISCONNECTED & events:
                clearfd(ev_fd,params,fd)
                logger.error("sock: %s error" % fd)
            elif ev_fd.EV_OUT & events:
                param = params.get(fd,None)
                if param == None:
                    continue
                writedata = param.get("writedata", "")
                if writedata == "":
                    clearfd(ev_fd,params,fd)
                    continue
                param["time"] = cur_time
                sendLen = param.get("writelen",0)
                total_write_len = len(writedata)
                cur_sock = param["connections"]
                f = param.get("f", None)
                totalsenlen = param.get("totalsenlen", None)
                while True:
                    try:
                        sendLen += cur_sock.send(writedata[sendLen:])
                        if sendLen == total_write_len:
                            if f != None and totalsenlen != None:
                                readmorelen = 102400
                                if readmorelen > totalsenlen:
                                    readmorelen = totalsenlen
                                morefiledata = ""
                                if readmorelen > 0:
                                    morefiledata = f.read(readmorelen)
                                if morefiledata != "":
                                    writedata = morefiledata
                                    sendLen = 0
                                    total_write_len = len(writedata)
                                    totalsenlen -= total_write_len
                                    param["writedata"] = writedata
                                    param["totalsenlen"] = totalsenlen
                                    continue
                                else:
                                    f.close()
                                    del param["f"]
                                    del param["totalsenlen"]
                            if param.get("keepalive", True):
                                param["writedata"] = ""
                                param["writelen"] = 0
                                ev_fd.modify(fd, ev_fd.EV_IN | ev_fd.EV_DISCONNECTED)
                                check_next_http(param, tp, ev_fd, fd, work)
                            else:
                                clearfd(ev_fd,params,fd)
                            break
                    except socket.error, msg:
                        if msg.errno == errno.EAGAIN or msg.errno == 10035:
                            param["writelen"] = sendLen
                            break
                        clearfd(ev_fd,params,fd)
                        break
            else:
                continue

        #check time out
        if cur_time - last_min_time > 600:
            last_min_time = cur_time
            objs = params.items()
            for (key_fd,value) in objs:
                fd_time = value.get("time", 0)
                del_time = cur_time - fd_time
                if del_time > 600:
                    clearfd(ev_fd,params,key_fd)
                elif fd_time < last_min_time:
                    last_min_time = fd_time


class WrapFastPyServer(object):
    def __init__(self,**kwargs):
        self.app=kwargs['app']
        CI['app']=self.app
        CI['router']=self.app.router
        CI['logger']=self.app.logger
        # globals()['logger']=self.app.logger
        # print(globals())
        self.port=self.app.config['server']['port']
        self.server_ip=self.app.config['server']['host']
        if 'cache_dir' in self.app.config['server']:
            read_cache_dir=self.app.config['server']['cache_dir']
            if not read_cache_dir.startswith('/'):
                static_dir=self.app.application_path+os.path.sep+read_cache_dir
        else:
            read_cache_dir=self.app.application_path+os.path.sep+'cache'
        if not os.path.exists(read_cache_dir):
            os.makedirs(read_cache_dir)
        if 'static_dir' in self.app.config['server']:
            static_dir=self.app.config['server']['static_dir']
            if not static_dir.startswith('/'):
                static_dir=self.app.application_path+os.path.sep+static_dir
        else:
            static_dir=self.app.application_path+os.path.sep+'static'
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        globals()['static_dir']=static_dir
        globals()['static_dir']=static_dir


    def start(self):
        self.init()
        run_main(self.listen_fd)

    def init(self):
        port=self.port
        self.listen_fd=None

        try:
            listen_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        except socket.error, msg:
            logger.error("create socket failed")
        try:
            listen_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error, msg:
            logger.error("setsocketopt SO_REUSEADDR failed")
        try:
            listen_fd.bind((self.server_ip, port))
        except socket.error as e:
            CI['logger'].error(e)
            logger.error("bind failed")
        try:
            listen_fd.listen(10240)
            listen_fd.setblocking(0)
        except socket.error, msg:
            logger.error(msg)

        child_num = cpu_count()
        c = 0
        while c < child_num:
            c = c + 1
            if 'Linux' in platform.system():
                newpid = os.fork()
                if newpid == 0:
                    run_main(listen_fd)
            else:
                pass
                #thread.start_new_thread(run_main, (listen_fd,))
        self.listen_fd=listen_fd


